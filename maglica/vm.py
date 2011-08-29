import maglica.dispatcher
import maglica.image
import libvirt
import maglica.config
import re

def clone(args): 
    images = maglica.image.list()
    host = ""
    for image in images:
        if args["image"] == image["name"]:
            host = image["host"]

    maglica.dispatcher.dispatch({
        "type"   : "vm",
        "action" : "clone",
        "host"   : host,
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
    dom = get_inactive_domain(args["name"])
    dom.create()

def stop(args):
    dom = get_active_domain(args["name"])
    dom.shutdown()

def get_active_domains():
    config = maglica.config.load()
    vms = []
    for host in config.hosts:
        conn = libvirt.open('remote://' + host)
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
        conn = libvirt.open('remote://' + host)
        domains = conn.listDefinedDomains()
        for domain in domains:
            if not re.match(r'.+[\.\-\_]original$', domain):
                vms.append({
                    "name"  : domain,
                    "state" : "shut off",
                    "host"  : host,
                    })
    return vms

def get_active_domain(name):
    config = maglica.config.load()
    for host in config.hosts:
        conn = libvirt.open('remote://' + host)
        ids = conn.listDomainsID()
        for id in ids:
            dom = conn.lookupByID(id)
            if name == dom.name():
                return dom

def get_inactive_domain(name):
    config = maglica.config.load()
    for host in config.hosts:
        conn = libvirt.open('remote://' + host)
        dom = conn.lookupByName(name)
        if dom:
            return dom
