import maglica.vm

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
