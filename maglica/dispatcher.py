import zmq
import json
import logging
logging.getLogger().setLevel(logging.DEBUG)

context = zmq.Context()

requestor = context.socket(zmq.REQ)
requestor.connect("tcp://localhost:5556")

def dispatch(args):
    requestor.send( json.dumps(args) )
    logging.info(requestor.recv())

