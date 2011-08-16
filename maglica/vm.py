import maglica.dispatcher
import maglica.image

def create(args): 
    images = maglica.image.list()
    host = ""
    for image in images:
        if args["image"] == image["name"]:
            host = image["host"]

    maglica.dispatcher.dispatch({
        "target" : "vm",
        "method" : "create",
        "host"   : host,
        "args"   : args,
        })
    
