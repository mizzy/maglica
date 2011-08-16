import libvirt
import maglica.config
import re

# Listing up "original" images
def list():
    config = maglica.config.load()
    images = []
    for host in config.hosts:
        conn = libvirt.open('remote://' + host)
        domains = conn.listDefinedDomains()
        for domain in domains:
            if re.match(r'.+[\.\-\_]original$', domain):
                images.append({
                    "name" : domain,
                    "host" : host,
                    })
    return images

def copy(args):
    pass

