def check_args(args, keys):
    if not isinstance(keys, list):
        keys = [ keys ]

    for key in keys:
        if not args.has_key(key):
            raise TypeError, ' '.join(keys)
        
