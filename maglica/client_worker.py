import zmq
import json
import logging

def main():
    context = zmq.Context()

    publisher = context.socket(zmq.PUB)
    publisher.bind("tcp://*:5555")

    replier = context.socket(zmq.REP)
    replier.bind("tcp://*:5556")

    while True:
        message = replier.recv()
        
        logging.info(message)

        args = json.loads(message)

        if args.has_key("host"):
            host = args["host"]
            publisher.send_multipart([
                str(host),
                json.dumps(args),
                ])
        
        replier.send('OK')
