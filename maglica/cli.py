import sys
import maglica.config
import maglica.images

def run_command(args):
    handlers = {
        'list': maglica.images.list
        }

    cmd = args.pop(0)

    if cmd not in handlers:
        return

    if len(args) > 0:
        options = {}
        for arg in args:
            try:
                ( key, value ) = arg.split('=')
            except ValueError:
                key   = arg
                value = True
                
            key = key.replace('--', '')
            print key
            print value
            options[key] = value
        handlers[cmd](options)
    else:
        handlers[cmd]()
    
def main():
    cfg = maglica.config.load()
    args = sys.argv[1:]
    run_command(args)
