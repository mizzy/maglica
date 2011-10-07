import zmq
import json
import logging
import maglica.config

cfg = maglica.config.load()
rep_port = "5556"
if cfg.client.has_key("rep_port"):
    rep_port = cfg.client["rep_port"]

context = zmq.Context()
requestor = context.socket(zmq.REQ)
requestor.connect(str("tcp://" + cfg.client["host"] + ":" + str(rep_port)))

def dispatch(args):
    requestor.send( json.dumps(args) )
    logging.info(requestor.recv())

