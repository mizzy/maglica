def check_args(args, options):
    for key in options["mandatory"]:
        if not args.has_key(key):
            raise MaglicaCliException, options
    return True


class MaglicaCliException(Exception):
    pass
