import maglica.vm
import re

def clone(args):
    maglica.vm.clone(args)
    
def list():
    required_params = "".split(' ')
    optional_params = "".split(' ')
    

    print "Name                               Host                 State"
    print "------------------------------------------------------------------------"

    vms = maglica.vm.list()
    for vm in vms:
        print "%-35s %-20s %-10s" % ( vm["name"], vm["host"], vm["state"] )

def start(args):
    maglica.vm.start(args)
    print "%s started" % ( args["name"] )

def stop(args):
    maglica.vm.stop(args)
    print "%s is being shutdown" % ( args["name"] )

def remove(args):
    maglica.vm.remove(args)
    print "%s is removed" % ( args["name"] )

def attach_disk(args):
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
    
    maglica.vm.attach_disk(args)
    print "Now attaching %sbytes disk to %s" % ( size, args["name"] )

