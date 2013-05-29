import libvirt
import maglica.config
import re
from xml.etree.ElementTree import *
import maglica.dispatcher
from maglica.util import check_args
import maglica.virt

# Listing up inactive images


def list():
    config = maglica.config.load()
    images = []
    for host in config.hosts:
        virt = maglica.virt.Virt()
        conn = libvirt.open(virt.uri(host["name"]))
        domains = conn.listDefinedDomains()
        for domain in domains:
            images.append({
                "name": domain,
                "host": host,
            })
    return images


def copy(args):
    options = {
        "mandatory": ["name", "dest"],
        "optional": [],
    }
    check_args(args, options)
    maglica.dispatcher.dispatch({
        "type": "image",
        "action": "copy",
        "args": {
            "name": args["name"],
            "dest": args["dest"],
        }
    })
