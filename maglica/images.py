import libvirt
import maglica.config

# Listing up "original" images
def list():
    config = maglica.config.load()
    images = []
    for host in config.hosts:
        print host
        conn = libvirt.open('remote://h011.southpark/')
        domains = conn.listDefinedDomains()
        for domain in domains:
            if domain
            images.append(domain)

    print images
