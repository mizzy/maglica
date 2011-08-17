import zmq
import socket
import maglica.host_worker.vm
import json
import logging
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')

def main(client):
    context = zmq.Context()
    
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("tcp://" + client + ":5555")
    subscriber.setsockopt(zmq.SUBSCRIBE, socket.gethostname())
    
    requestor = context.socket(zmq.REQ)
    requestor.connect("tcp://" + client + ":5556")

    while True:
        [address, args] = subscriber.recv_multipart()
        args = json.loads(args)
        cmd = eval("maglica.host_worker." + args["target"] + "." + args["method"])
        ret = cmd(args["args"])
        requestor.send( json.dumps({ "message" : ret }) )
        logging.info(requestor.recv())

    requestor.close()
    subscriber.close()
    context.term()
