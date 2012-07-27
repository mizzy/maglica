import zmq
import maglica.config
import json
import logging
import libvirt
import subprocess 
from xml.etree.ElementTree import *
import maglica.virt

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

    logging.info("copy worker started.")

    virt = maglica.virt.Virt()

    while True:
        [address, args] = subscriber.recv_multipart()
        args = json.loads(args)

        name = args["name"]
        dest = args["dest"]

        conn = libvirt.open(virt.uri(dest))
        domain_found = 1
        try:
            conn.lookupByName(name)
        except:
            domain_found = 0

        if domain_found:
            requestor.send(json.dumps({
                "message"    : "%s already exsits on %s" % ( name, dest),
                "status"     : 2,
                "request_id" : args["request_id"],
                }))
            res = requestor.recv()
            break
        
        src = None
        config = maglica.config.load()
        for host in config.hosts:
            domain = None
            host = host["name"]
            conn = libvirt.open(virt.uri(host))
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

                logging.info( "copying %s from %s to %s" % ( file, src, dest ) )
                proc = subprocess.Popen(cmdline1, stdout=subprocess.PIPE)
                subprocess.call(cmdline2, stdin=proc.stdout)

        conn = libvirt.open(virt.uri(dest))
        conn.defineXML(xml)        

        message = "Done copying %s from %s to %s" % ( file, src, dest )
        logging.info(message)
        requestor.send(json.dumps({
            "message"    : message,
            "status"     : 1,
            "request_id" : args["request_id"],
        }))
        res = requestor.recv()
        if res:
            logging.info(res)

    requestor.close()
    subscriber.close()
    context.term()
