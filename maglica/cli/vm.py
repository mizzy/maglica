import maglica.vm
import re


def clone(args):
    if args.has_key("start"):
        start = args["start"]
    else:
        start = True

    if start == 0 or start == "false" or start == "False":
        args["start"] = False
    else:
        args["start"] = True

    maglica.vm.clone(args)


def attach_iso(args):
    maglica.vm.attach_iso(args)


def set_boot_device(args):
    maglica.vm.set_boot_device(args)


def list(args):
    required_params = "".split(' ')
    optional_params = "".split(' ')

    print "Name                               Host                 State"
    print "------------------------------------------------------------------------"

    vms = maglica.vm.list()
    for vm in vms:
        print "%-35s %-20s %-10s" % (vm["name"], vm["host"], vm["state"])


def start(args):
    maglica.vm.start(args)
    print "%s started" % (args["name"])


def stop(args):
    maglica.vm.stop(args)
    print "%s is being shutdown" % (args["name"])


def destroy(args):
    maglica.vm.destroy(args)
    print "%s is being destroyed" % (args["name"])


def remove(args):
    maglica.vm.remove(args)
    print "%s is removed" % (args["name"])


def attach_disk(args):
    maglica.vm.attach_disk(args)
    print "Now attaching %sbytes disk to %s" % (args["size"], args["name"])


def set_vcpus(args):
    maglica.vm.set_vcpus(args)
    vcpus = args["vcpus"]
    name = args["name"]
    print "Set %s vcpus to %s.Please stop and start %s if it is runnging." % (vcpus, name, name)


def set_memory(args):
    maglica.vm.set_memory(args)
    print "Set %sbytes memory to %s.Please stop and start %s if it is runnging." % (args["size"], args["name"], args["name"])


def console(args):
    maglica.vm.console(args)
