import zmq
import socket
import maglica.host_worker.vm
import json
import logging
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
import maglica.config

def main():
    context = zmq.Context()

    cfg = maglica.config.load()
    pub_port = "5555"
    if cfg.client.has_key("pub_port"):
        pub_port = cfg.client["pub_port"]

    rep_port = "5556"
    if cfg.client.has_key("rep_port"):
        rep_port = cfg.client["rep_port"]

    subscriber = context.socket(zmq.SUB)
    subscriber.connect(str("tcp://" + cfg.client["host"] + ":" + pub_port))
    subscriber.setsockopt(zmq.SUBSCRIBE, socket.gethostname())
    
    requestor = context.socket(zmq.REQ)
    requestor.connect(str("tcp://" + str(cfg.client["host"]) + ":" + rep_port))

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
