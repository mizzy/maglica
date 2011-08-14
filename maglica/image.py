import libvirt
import maglica.config

# Listing up "original" images
def list():
    print "Name                           Host"
    print "--------------------------------------"
    config = maglica.config.load()
    images = []
    for host in config.hosts:
        conn = libvirt.open('remote://' + host)
        domains = conn.listDefinedDomains()
        for domain in domains:
            print "%-30s %-30s" % ( domain, host )

def copy(args):
    # image
    # hostname
    pass

