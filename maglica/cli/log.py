import maglica.request_log
import maglica.util

def status(args):
    maglica.util.check_args(args, "id")
    request_log = maglica.request_log.RequestLog()

    row = request_log.get_status(args["id"])

    status  = row["status"]
    args    = row["args"]
    message = row["message"]
    
    if status == 0:
        print "In progress: %s" % args
    elif status == 1:
        print "Completed: %s, message: %s" % ( args, message )
    elif status == 2:
        print "Error: %s" % message
