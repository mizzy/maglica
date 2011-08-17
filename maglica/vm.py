import maglica.dispatcher
import maglica.image

def clone(args): 
    images = maglica.image.list()
    host = ""
    for image in images:
        if args["image"] == image["name"]:
            host = image["host"]

    maglica.dispatcher.dispatch({
        "target" : "vm",
        "method" : "clone",
        "host"   : host,
        "args"   : args,
        })
    
