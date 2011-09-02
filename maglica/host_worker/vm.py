import subprocess
import socket
import guestfs
import re
import libvirt
from xml.etree.ElementTree import *
import logging
import os

def clone(args):
    image      = args["image"]
    hostname   = args["hostname"]

    conn = libvirt.open(None)
    dom  = conn.lookupByName(image)
    desc = fromstring(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))

    for disk in desc.findall(".//disk"):
        if disk.get("device") == "disk":
            source = disk.find(".//source").get("file")

    image_file = source.replace(image, hostname)

    cmdline = [
        "virt-clone",
        "-o",
        image,
        "-n",
        hostname,
        "-f",
        image_file,
        ]
    proc = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    
    message = None
    status  = 1
    if proc.returncode:
        status = 2
        message = stderr
        
    g = guestfs.GuestFS()
    g.add_drive(image_file)
    g.launch()
    filesystems = g.list_filesystems()
    for filesystem in filesystems:
        if re.match(r'.+root$', filesystem[0]) or re.match(r'.+LogVol00$', filesystem[0]) or filesystem[0] == '/dev/vda1':
            fs = filesystem[0]

    g.mount(fs, '/')

    ostype = None
    if g.is_file('/etc/redhat-release'):
        ostype = 'redhat'
    elif g.is_file('/etc/debian_version'):
        ostype = 'debian'

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
    elif ostype == 'debian':
        g.write_file('/etc/hosts', '127.0.0.1    localhost', 0)
        g.write_file('/etc/hostname', hostname, 0)

    g.sync()
    g.umount_all()

    dom = conn.lookupByName(hostname)
    dom.create()
    
    if status == 1:
        message = "Created %s successfully on %s" % ( image, hostname )
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
            print file
            os.remove(file)

    dom.undefine()


    return {
        "message" : "%s removed successfully" % args["name"],
        "status"  : 1,
    }
