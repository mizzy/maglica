import sys
import re
import maglica.config
import maglica.cli
import maglica.cli.image
import maglica.cli.vm
import maglica.cli.log

OBJECT_TYPES = filter(
    lambda x: not re.match(r"^__", x) and x != 'dispatcher',
    dir(maglica.cli)
)

def run_command(args):
    type  = args.pop(0)
    action = args.pop(0)
    cmd = eval("maglica.cli." + type + "." + action)
    
    if len(args) > 0:
        options = {}
        for arg in args:
            try:
                ( key, value ) = arg.split('=')
            except ValueError:
                key   = arg
                value = True
                
            key = key.replace('--', '')
            options[key] = value
        cmd(options)
    else:
        cmd()

def get_object_type(args):
    """
    If this is a CLI command about an object type, e.g. "maglica vm list", return the type, like "vm"
    """
    if len(args) < 1:
        return None
    elif args[0] in OBJECT_TYPES:
        return args[0]
    return None

def get_object_actions(object_type):
    actions = filter(
        lambda x: not re.match(r"^__", x) and x != 'maglica' and x != 're',
        eval("dir(maglica.cli." + object_type + ")")
    )
    return actions
    
def get_object_action(object_type, args):
    actions = get_object_actions(object_type)
    if len(args) < 2:
        return None
    elif args[1] in actions:
        return args[1]
    return None

def print_help():
    """
    Prints general-top level help, e.g. "maglica --help" or "maglica" or "maglcica command-does-not-exist"
    """
    print "usage\n====="
    print "maglica <" + ('|').join(OBJECT_TYPES) + "> ..."
    exit(1)

def print_object_help(object_type):
    actions = get_object_actions(object_type)
    print "usage"
    print "====="
    for action in actions:
        action = action.replace('_', '-')
        print "maglica %s %s" % ( object_type, action) 
    exit(1)

def main():
    args = sys.argv[1:]
    if len(args) > 1:
        args[1] = args[1].replace('-', '_')
    object_type   = get_object_type(args)

    if len(sys.argv) < 2 or sys.argv[1] == "--help" or not object_type:
        print_help()

    object_action = get_object_action(object_type, args)
    if not object_action:
        print_object_help(object_type)

    run_command(args)
