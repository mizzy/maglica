import zmq
import json
import maglica.config
import logging
from maglica.request_log import RequestLog


def main():
    context = zmq.Context()

    request_log = RequestLog()

    cfg = maglica.config.load()
    pub_port = "5555"
    if cfg.client.has_key("pub_port"):
        pub_port = str(cfg.client["pub_port"])

    rep_port = "5556"
    if cfg.client.has_key("rep_port"):
        rep_port = str(cfg.client["rep_port"])

    publisher = context.socket(zmq.PUB)
    publisher.bind(str("tcp://*:" + pub_port))

    replier = context.socket(zmq.REP)
    replier.bind(str("tcp://*:" + rep_port))

    logging.info("client worker started.")

    while True:
        message = replier.recv()
        logging.info(message)

        args = json.loads(message)

        if args.has_key("host"):
            host = args["host"]
            args["request_id"] = request_log.insert_request(args)
            publisher.send_multipart([
                str(host),
                json.dumps(args),
            ])
            replier.send(str(
                "request id: %d, sent %s %s request to %s"
                % (args["request_id"], args["type"], args["action"], args["host"])
            ))

        elif args.has_key("type") and args["type"] == "image" and args["action"] == "copy":
            args["args"]["request_id"] = request_log.insert_request(args)
            publisher.send_multipart([
                'copy',
                json.dumps(args["args"]),
            ])
            replier.send("request id: %d, sent image copy requst to copy worker" %
                         args["args"]["request_id"])
        elif args.has_key("status"):
            request_log.update_status(args[
                                      "request_id"], args["status"], args["message"])
            replier.send('')
        else:
            replier.send('')
