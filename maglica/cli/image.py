import maglica.image


def list(args):
    print "Name                                     Host"
    print "---------------------------------------------------------"
    images = maglica.image.list()
    for image in images:
        print "%-40s %-30s" % (image["name"], image["host"]["name"])


def copy(args):
    maglica.image.copy(args)
