import maglica.dispatcher
import maglica.image
import libvirt
import maglica.config
import re
import random
import sys
from xml.etree.ElementTree import *
import subprocess
from maglica.util import check_args

def info(args):
    options = {
        "mandatory": ["name"],
        "optional" : [],
    }
    check_args(args, options)
    name = args["name"]
    (dom, host) = get_active_domain(name)
    cmdline = ["virsh", "--connect", "remote://" + host, "vncdisplay", name]
    p = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
    out = p.stdout.readline().rstrip()
    return {
        "name"   : name,
        "host"   : host,
        "vncport": 5900 + int(out.replace(":", ""))
    }

    
def clone(args): 
    options = {
        "mandatory": ["image", "hostname"],
        "optional" : ["start"],
    }
    check_args(args, options)

    images = maglica.image.list()
    hosts = []

    for image in images:
        if args["image"] == image["name"]:
            hosts.append(image["host"])

    if len(hosts) < 1:
        raise Exception('Image "%s" is active or not exist.' % args["image"])
    
    maglica.dispatcher.dispatch({
        "type"   : "vm",
        "action" : "clone",
        "host"   : hosts[random.randint(0, len(hosts) - 1)],
        "args"   : args,
    })

def list():
    vms = []
    for vm in get_active_domains():
        vms.append(vm)
    for vm in get_inactive_domains():
        vms.append(vm)
    return vms

def start(args):
    options = {
        "mandatory": ["name"],
        "optional" : [],
    }
    check_args(args, options)
    dom = get_inactive_domain(args["name"])
    if dom:
        conn = libvirt.open("remote://" + dom["host"])
        dom  = conn.lookupByName(dom["name"])
        dom.create()
    else:
        raise Exception("%s not found or already started." % args["name"])

def stop(args):
    options = {
        "mandatory": ["name"],
        "optional" : [],
    }
    check_args(args, options)
    (dom, host) = get_active_domain(args["name"])
    if dom:
        dom.shutdown()
    else:
        raise Exception("%s not found or already stopped." % args["name"])

def destroy(args):
    options = {
        "mandatory": ["name"],
        "optional" : [],
    }
    check_args(args, options)
    (dom, host) = get_active_domain(args["name"])
    if dom:
        dom.destroy()
    else:
        raise Exception("%s not found or already destroyed." % args["name"])

def remove(args):
    options = {
        "mandatory": ["name"],
        "optional" : [],
    }
    check_args(args, options)
    name = args["name"]
    dom = get_inactive_domain(name)

    if not dom:
        (dom, host) = get_active_domain(name)
        if dom:
            raise Exception("Active domain cannot be removed.Please stop it.")
        else:
            raise Exception("Domain not found.")

    maglica.dispatcher.dispatch({
        "type"   : "vm",
        "host"   : dom["host"],
        "action" : "remove",
        "args"   : args,
    })

def attach_iso(args):
    options = {
        "mandatory": ["name", "iso"],
        "optional" : [],
    }
    check_args(args, options)

    name = args["name"]
    iso  = args["iso"]

    (dom, host) = get_active_domain(name)
    if not dom:
        dom  = get_inactive_domain(name)
        host = dom["host"]

    conn = libvirt.open("remote://" + host)
    dom  = conn.lookupByName(name)

    cdrom = None
    desc = fromstring(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
    for disk in desc.findall(".//disk"):
        if disk.get("device") == "cdrom":
            cdrom = disk
            if cdrom.find(".//source"):
                cdrom.find(".//source").set("file", iso)
            else:
                desc.find(".//devices").remove(cdrom)
                cdrom = None

    if not cdrom:
        xml = """
<disk type="file" device="cdrom">
  <driver name="qemu"/>
  <source file="%s" />
  <target dev="hdc" bus="ide"/>
  <readonly/>
</disk>
   """
        xml = xml % ( iso )
        desc.find(".//devices").insert(-1, fromstring(xml))

    conn.defineXML(tostring(desc))

def set_boot_device(args):
    options = {
        "mandatory": ["name", "dev"],
        "optional" : [],
    }
    check_args(args, options)
     
    name = args["name"]
    dev  = args["dev"]

    (dom, host) = get_active_domain(name)
    if not dom:
        dom  = get_inactive_domain(name)
        host = dom["host"]

    conn = libvirt.open("remote://" + host)
    dom  = conn.lookupByName(name)

    desc = fromstring(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
    desc.find(".//boot").set("dev", dev)

    conn.defineXML(tostring(desc))

def attach_disk(args):
    options = {
        "mandatory": ["name", "size"],
        "optional" : [],
    }
    check_args(args, options)

    size = args["size"]
    if re.match(r'.+G$', size):
        args["size"] = int(args["size"][:-1])
        args["size"] = args["size"] * 1024 * 1024
    elif re.match(r'.+M$', size):
        args["size"] = int(args["size"][:-1])
        args["size"] = args["size"] * 1024
    elif re.match(r'.+K$', size):
        args["size"] = int(args["size"][:-1])

    if args["size"] > 100 * 1024 * 1024:
        raise Exception("Size is too large.")

    name = args["name"]
    (dom, host) = get_active_domain(name)
    maglica.dispatcher.dispatch({
        "type"   : "vm",
        "host"   : host,
        "action" : "attach_disk",
        "args"   : args,
    })

def set_vcpus(args):
    options = {
        "mandatory": ["name", "vcpus"],
        "optional" : [],
    }
    check_args(args, options)

    name  = args["name"]
    vcpus = args["vcpus"]

    (dom, host) = get_active_domain(name)
    if not dom:
        dom  = get_inactive_domain(name)
        host = dom["host"]

    conn = libvirt.open("remote://" + host)
    dom  = conn.lookupByName(name)

    desc = fromstring(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
    desc.find(".//vcpu").text = vcpus
    conn.defineXML(tostring(desc))

def set_memory(args):
    options = {
        "mandatory": ["name", "size"],
        "optional" : [],
    }
    check_args(args, options)

    name = args["name"]
    size = args["size"]

    if re.match(r'.+G$', size):
        args["size"] = int(args["size"][:-1])
        args["size"] = args["size"] * 1024 * 1024
    elif re.match(r'.+M$', size):
        args["size"] = int(args["size"][:-1])
        args["size"] = args["size"] * 1024
    elif re.match(r'.+K$', size):
        args["size"] = int(args["size"][:-1])

    if args["size"] > 10 * 1024 * 1024:
        raise Exception("Size is too large.")

    (dom, host) = get_active_domain(name)
    if not dom:
        dom  = get_inactive_domain(name)
        host = dom["host"]

    conn = libvirt.open("remote://" + host)
    dom  = conn.lookupByName(name)

    desc = fromstring(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
    desc.find(".//memory").text = str(size)
    desc.find(".//currentMemory").text = str(size)
    conn.defineXML(tostring(desc))

def console(args):
    options = {
        "mandatory": ["name"],
        "optional" : [],
    }
    check_args(args, options)
    name = args["name"]
    (dom, host) = get_active_domain(name)
    subprocess.call(["virsh", "--connect", "remote://" + host, "console", name])

def get_active_domains():
    config = maglica.config.load()
    vms = []
    for host in config.hosts:
        conn = libvirt.open("remote://" + host)
        ids = conn.listDomainsID()
        for id in ids:
            dom = conn.lookupByID(id)
            vms.append({
                "name"  : dom.name(),
                "state" : "running",
                "host"  : host,
                })
    return vms

def get_inactive_domains():
    config = maglica.config.load()
    vms = []
    for host in config.hosts:
        conn = libvirt.open("remote://" + host)
        domains = conn.listDefinedDomains()
        for domain in domains:
            vms.append({
                "name"  : domain,
                "state" : "shut off",
                "host"  : host,
            })
    return vms

def get_active_domain(name):
    config = maglica.config.load()
    for host in config.hosts:
        conn = libvirt.open("remote://" + host)
        ids = conn.listDomainsID()
        for id in ids:
            dom = conn.lookupByID(id)
            if name == dom.name():
                return ( dom, host )
    return (None, None)

def get_inactive_domain(name):
    domains = get_inactive_domains()
    for domain in domains:
        if name == domain["name"]:
            return domain
