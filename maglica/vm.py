import maglica.dispatcher
import maglica.image
import maglica.config
import re
import random
import sys
from maglica.util import check_args
from maglica.virt import Virt


def info(args):
    options = {
        "mandatory": ["name"],
        "optional": [],
    }
    check_args(args, options)

    virt = Virt(hosts())
    return virt.info(args["name"])


def clone(args):
    virt = Virt(hosts())

    options = {
        "mandatory": ["image", "hostname"],
        "optional": ["on", "start", "format"],
    }
    check_args(args, options)

    images = maglica.image.list()
    target_hosts = []

    for image in images:
        if args["image"] == image["name"]:
            target_hosts.append(image["host"])

    if len(target_hosts) < 1:
        raise Exception('Image "%s" is active or not exist.' % args["image"])

    if args.has_key("on"):
        host = args["on"]
    else:
        min = 65535
        for target_host in target_hosts:
            size = len(virt.get_active_domains_of(
                target_host["name"])) * 10 / target_host["weight"]
            if size < min:
                min = size
                host = target_host["name"]

    maglica.dispatcher.dispatch({
        "type": "vm",
        "action": "clone",
        "host": host,
        "args": args,
    })


def list():
    virt = Virt(hosts())
    return virt.get_domains()


def start(args):
    options = {
        "mandatory": ["name"],
        "optional": [],
    }
    check_args(args, options)

    virt = Virt(hosts())
    virt.start(args["name"])


def stop(args):
    options = {
        "mandatory": ["name"],
        "optional": [],
    }
    check_args(args, options)

    virt = Virt(hosts())
    virt.stop(args["name"])


def destroy(args):
    options = {
        "mandatory": ["name"],
        "optional": [],
    }
    check_args(args, options)

    virt = Virt(hosts())
    virt.destroy(args["name"])


def remove(args):
    options = {
        "mandatory": ["name"],
        "optional": ["on"],
    }
    check_args(args, options)
    name = args["name"]

    virt = Virt(hosts())
    dom = virt.get_inactive_domain(name)

    if not dom:
        (dom, host) = virt.get_active_domain(name)
        if dom:
            raise Exception("Active domain cannot be removed.Please stop it.")
        else:
            raise Exception("Domain not found.")

    host = dom["host"]
    if args.has_key("on"):
        host = args["on"]

    maglica.dispatcher.dispatch({
        "type": "vm",
        "host": host,
        "action": "remove",
        "args": args,
    })


def attach_iso(args):
    options = {
        "mandatory": ["name", "iso"],
        "optional": [],
    }
    check_args(args, options)

    name = args["name"]
    iso = args["iso"]

    virt = Virt(hosts())
    virt.attach_iso(name, iso)


def set_boot_device(args):
    options = {
        "mandatory": ["name", "dev"],
        "optional": [],
    }
    check_args(args, options)

    virt = Virt(hosts())
    virt.set_boot_device(args["name"], args["dev"])


def attach_disk(args):
    options = {
        "mandatory": ["name", "size"],
        "optional": [],
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
    virt = Virt(hosts())
    (dom, host) = virt.get_active_domain(name)
    maglica.dispatcher.dispatch({
        "type": "vm",
        "host": host,
        "action": "attach_disk",
        "args": args,
    })


def set_vcpus(args):
    options = {
        "mandatory": ["name", "vcpus"],
        "optional": [],
    }
    check_args(args, options)

    virt = Virt(hosts())
    virt.set_vcpus(args["name"], args["vcpus"])


def set_memory(args):
    options = {
        "mandatory": ["name", "size"],
        "optional": [],
    }
    check_args(args, options)

    name = args["name"]
    size = args["size"]

    if re.match(r'.+G$', size):
        size = int(size[:-1])
        size = size * 1024 * 1024
    elif re.match(r'.+M$', size):
        size = int(size[:-1])
        size = size * 1024
    elif re.match(r'.+K$', size):
        size = int(size[:-1])

    if size > 10 * 1024 * 1024:
        raise Exception("Size is too large.")

    virt = Virt(hosts())
    virt.set_memory(name, size)


def console(args):
    options = {
        "mandatory": ["name"],
        "optional": [],
    }
    check_args(args, options)

    virt = Virt(hosts())
    virt.console(args["name"])


def hosts():
    return maglica.config.load().hosts
