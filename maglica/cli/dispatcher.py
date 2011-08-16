import sys
import maglica.config
import maglica.cli.image
import maglica.cli.vm

def run_command(args):
    target = args.pop(0)
    method = args.pop(0)
    cmd = eval("maglica.cli." + target + "." + method)
    
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

def main():
    cfg = maglica.config.load()
    args = sys.argv[1:]
    run_command(args)
