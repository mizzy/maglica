import maglica.dispatcher
import maglica.image
import libvirt
import maglica.config
import re
import random
import sys

def clone(args): 
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
    dom = get_inactive_domain(args["name"])
    if dom:
        conn = libvirt.open("remote://" + dom["host"])
        dom  = conn.lookupByName(dom["name"])
        dom.create()
    else:
        raise Exception("%s not found." % args["name"])

def stop(args):
    dom = get_active_domain(args["name"])
    dom.shutdown()

def remove(args):
    name = args["name"]
    dom = get_inactive_domain(name)

    if not dom:
        dom = get_active_domain(name)
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
    domains = get_inactive_domains()
    for domain in domains:
        if name == domain["name"]:
            return domain

