import zmq
import maglica.config
import json
import logging
import libvirt
import maglica.util
import subprocess 
from xml.etree.ElementTree import *

def main():
    context = zmq.Context()

    config = maglica.config.load()
    pub_port = "5555"
    if config.client.has_key("pub_port"):
        pub_port = config.client["pub_port"]

    rep_port = "5556"
    if config.client.has_key("rep_port"):
        rep_port = config.client["rep_port"]

    subscriber = context.socket(zmq.SUB)
    subscriber.connect(str("tcp://" + config.client["host"] + ":" + pub_port))
    subscriber.setsockopt(zmq.SUBSCRIBE, 'copy')
    
    requestor = context.socket(zmq.REQ)
    requestor.connect(str("tcp://" + config.client["host"] + ":" + rep_port))

    while True:
        [address, args] = subscriber.recv_multipart()
        args = json.loads(args)

        name = args["name"]
        dest = args["dest"]

        src = None
        config = maglica.config.load()
        for host in config.hosts:
            domain = None
            conn = libvirt.open('remote://' + host)
            try:
                domain = conn.lookupByName(name)
            except:
                pass
            if domain:
                src = host
                xml = domain.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE)
                break

        if not src:
            requestor.send( json.dumps({ "message" : "%s not found on any hosts." % name }) )
            logging.info(requestor.recv())
            continue

        desc = fromstring(xml)
        for disk in desc.findall(".//disk"):
            if disk.get("device") == "disk":
                file = disk.find(".//source").get("file")
                cmdline1 = [
                    'ssh',
                    src,
                    'dd',
                    'if=' + file,
                ]
                cmdline2 = [
                    'ssh',
                    dest,
                    'dd',
                    'of=' + file,
                ]

                logging.info(' '.join(cmdline1))
                logging.info(' '.join(cmdline2))

                proc = subprocess.Popen(cmdline1, stdout=subprocess.PIPE)
                subprocess.call(cmdline2, stdin=proc.stdout)
                
        conn = libvirt.open('remote://' + dest)
        conn.defineXML(xml)        
        
        requestor.send( json.dumps({ "message" : "copy done" }) )
        logging.info(requestor.recv())

    requestor.close()
    subscriber.close()
    context.term()
