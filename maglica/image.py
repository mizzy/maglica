import libvirt
import maglica.config
import re

# Listing up "original" images
def list():
    print "Name                                     Host"
    print "---------------------------------------------------------"
    config = maglica.config.load()
    images = []
    for host in config.hosts:
        conn = libvirt.open('remote://' + host)
        domains = conn.listDefinedDomains()
        for domain in domains:
            if re.match(r'.+[\.\-\_]original$', domain):
                print "%-40s %-30s" % ( domain, host )

def copy(args):
    pass

