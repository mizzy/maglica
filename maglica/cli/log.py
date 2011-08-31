import maglica.request_log

def status(args):
    request_log = maglica.request_log.RequestLog()

    row = request_log.get_status(args["id"])

    status  = row["status"]
    args    = row["args"]
    message = row["message"]
    
    if status == 0:
        print "In progress: %s" % args
    elif status == 1:
        print "Completed: %s" % args
    elif status == 2:
        print "Error: %s" % message
