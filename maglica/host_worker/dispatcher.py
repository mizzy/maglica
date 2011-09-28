import zmq
import socket
import maglica.host_worker.vm
import json
import maglica.config
import logging

def main():
    context = zmq.Context()

    cfg = maglica.config.load()
    pub_port = "5555"
    if cfg.client.has_key("pub_port"):
        pub_port = str(cfg.client["pub_port"])

    rep_port = "5556"
    if cfg.client.has_key("rep_port"):
        rep_port = str(cfg.client["rep_port"])

    subscriber = context.socket(zmq.SUB)
    subscriber.connect(str("tcp://" + cfg.client["host"] + ":" + pub_port))
    subscriber.setsockopt(zmq.SUBSCRIBE, socket.gethostname())
    
    requestor = context.socket(zmq.REQ)
    requestor.connect(str("tcp://" + cfg.client["host"] + ":" + rep_port))

    logging.info("host worker started.")
    
    while True:
        [address, args] = subscriber.recv_multipart()
        logging.info(args)
        args = json.loads(args)
        cmd = eval("maglica.host_worker." + args["type"] + "." + args["action"])
        ret = cmd(args["args"])
        ret["request_id"] = args["request_id"]
        requestor.send(json.dumps(ret))

        res = requestor.recv()
        if res:
            logging.info(res)

    requestor.close()
    subscriber.close()
    context.term()
