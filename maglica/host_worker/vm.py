# -*- coding: utf-8 -*-

import subprocess
import socket
import guestfs
import re
import libvirt
from xml.etree.ElementTree import *
import logging
import os
import time

def clone(args):
    image    = args["image"]
    hostname = args["hostname"]

    format = None
    if args.has_key("format"):
        format = args["format"]

    conn = libvirt.open(None)
    dom  = conn.lookupByName(image)
    desc = fromstring(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))

    sources = []
    for disk in desc.findall(".//disk"):
        if disk.get("device") == "disk":
            sources.append(disk.find(".//source").get("file"))

    target_paths = []
    for source in sources:
        target_file = os.path.basename(source)
        target_file = target_file.replace(image, hostname)
        target_dir = _select_most_free_dir(conn)
        if not target_dir:
            target_dir = os.path.dirname(source)

        target_paths.append(os.path.join(target_dir, target_file))

    cmdline = [
        "virt-clone",
        "-o",
        image,
        "-n",
        hostname,
    ]

    for path in target_paths:
        cmdline.append("-f")
        cmdline.append(path)

    proc = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    message = None
    status  = 1
    if proc.returncode:
        status = 2
        message = stderr
        
    g = guestfs.GuestFS()
    for path in target_paths:
        g.add_drive(path)
    g.launch()

    roots       = g.inspect_os()
    mountpoints = g.inspect_get_mountpoints(roots[0])

    for mountpoint in mountpoints:
        g.mount(mountpoint[1], mountpoint[0])

    ostype = None
    if g.is_file('/etc/redhat-release'):
        ostype = 'redhat'
    elif g.is_file('/etc/debian_version'):
        ostype = 'debian'

    ### TODO: OS 毎に別モジュールにする
    if ostype == 'redhat':
        ifcfg='''DEVICE=%s
BOOTPROTO=dhcp
ONBOOT=yes
TYPE="Ethernet"
DHCP_HOSTNAME=%s
'''

        network='''NETWORKING=yes
HOSTNAME=%s
'''

        ifcfg0  = ifcfg % ('eth0', hostname)
        network = network % ( hostname )

        g.write_file('/etc/sysconfig/network-scripts/ifcfg-eth0', ifcfg0, 0)
        g.write_file('/etc/sysconfig/network', network, 0)
        g.write_file('/etc/udev/rules.d/70-persistent-net.rules', '', 0)

        if g.exists('/etc/sysconfig/network-scripts/ifcfg-eth1'):
            ifcfg1 = ifcfg % ('eth1', re.sub(r"\.pb$", ".pblan", hostname))
            g.write_file('/etc/sysconfig/network-scripts/ifcfg-eth1', ifcfg1, 0)

    elif ostype == 'debian':
        g.write_file('/etc/hosts', '127.0.0.1    localhost', 0)
        g.write_file('/etc/hostname', hostname, 0)
        g.write_file('/etc/udev/rules.d/70-persistent-net.rules', '', 0)

    shadow = g.read_file("/etc/shadow")
    g.write_file("/etc/shadow", re.sub(r"^root:[^:]+:", "root:$1$ZJsvbRbB$dWzQZuu8dDFR8wr6PTPjp0:", shadow), 0)

    if format == "vmdk":
        grub = g.read_file("/boot/grub/grub.conf")
        g.write_file("/boot/grub/grub.conf", re.sub(r"console=[^\s]+", "", grub), 0)

    g.sync()
    g.umount_all()

    dom = conn.lookupByName(hostname)
    if args["start"] and format != "vmdk":
        dom.create()

    if format == "vmdk":
        vmdk_path = "/var/www/html/maglica/%s.vmdk" % hostname
        cmdline = [
            "qemu-img",
            "convert",
            "-f",
            "raw",
            "-O",
            "vmdk",
            target_paths[0],
            vmdk_path,
            ]

        proc = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()

        if proc.returncode:
            status = 2
            message = stderr
        else:
            message = "Get vmdk file from http://%s/maglica/%s.vmdk" % ( socket.gethostname(), hostname )

        remove({"name": hostname})

    if status == 1 and not message:
        message = "%s was cloned from %s on %s successfully"  % ( hostname, image, socket.gethostname() )

    return {
        "message": message,
        "status" : status,
    }


def remove(args):
    conn = libvirt.open(None)
    dom  = conn.lookupByName(args["name"])
    desc = fromstring(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))

    for disk in desc.findall(".//disk"):
        if disk.get("device") == "disk":
            file = disk.find(".//source").get("file")
            os.remove(file)

    dom.undefine()

    return {
        "message" : "%s removed successfully" % args["name"],
        "status"  : 1,
    }

def attach_disk(args):
    conn = libvirt.open(None)
    name = args["name"]
    size = int(args["size"])
    dom = conn.lookupByName(name)

    devs = []
    desc = fromstring(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
    for disk in desc.findall(".//disk"):
        if disk.get("device") == "disk":
            dev = disk.find(".//target").get("dev")
            if re.match(r'^vd', dev):
                devs.append(dev)

    devs.sort()
    if len(devs) > 0:
        dev = devs[-1]
        last_char = chr(ord(dev[-1])+1)
        dev = 'vd' + last_char
    else:
        dev = 'vda'

    dir = _select_most_free_dir(conn)
    if not dir:
        dir = "/var/lib/libvirt/images"

    path = os.path.join(dir, name + "-" + str(time.time()))

    _create_raw_image(path, size)

    xml = '''
<disk type='file' device='disk'>
  <driver name='qemu' type='raw' cache='none'/>
  <source file='%s' />
  <target dev='%s' bus='virtio'/>
</disk>
    '''

    xml = xml % (path, dev)

    dom.attachDevice(xml)

    desc.find(".//devices").insert(-1, fromstring(xml))
    conn.defineXML(tostring(desc))

    return {
        "message" : "%s kbytes disk attached to %s as /dev/%s successfully" % ( size, name, dev ),
        "status"  : 1,
    }


def _select_most_free_dir(conn):
    current_free_size = 0
    pools = conn.listStoragePools()
    most_free_dir = None
    for pool in pools:
        desc = fromstring(conn.storagePoolLookupByName(pool).XMLDesc(0))
        path = desc.find(".//path").text
        s = os.statvfs(path)
        free_size = s.f_bsize * s.f_bfree
        if free_size > current_free_size:
            most_free_dir = path

        current_free_size = free_size

    return most_free_dir

def _create_raw_image(path, size):
    cmd = ['dd', 'if=/dev/zero', 'of=%s' % path, 'bs=1024', 'count=%d' % size]
    proc = subprocess.call(cmd)
