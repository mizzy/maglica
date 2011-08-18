import zmq
import json
import logging
import maglica.config

def main():
    context = zmq.Context()

    cfg = maglica.config.load()
    pub_port = 5555
    if cfg.client.has_key("pub_port"):
        pub_port = cfg.client["pub_port"]

    rep_port = 5556
    if cfg.client.has_key("rep_port"):
        rep_port = cfg.client["rep_port"]

    publisher = context.socket(zmq.PUB)
    publisher.bind(str("tcp://*:" + pub_port))

    replier = context.socket(zmq.REP)
    replier.bind(str("tcp://*:" + rep_port))

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
