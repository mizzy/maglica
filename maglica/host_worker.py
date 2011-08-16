import zmq
import socket

def main():
    context = zmq.Context()

    subscriber = context.socket(zmq.SUB)
    subscriber.connect("tcp://192.168.10.39:5555")
    subscriber.setsockopt(zmq.SUBSCRIBE, socket.gethostname())
    
    requestor = context.socket(zmq.REQ)
    requestor.connect("tcp://192.168.10.39:5556")

    while True:
        [address, content] = subscriber.recv_multipart()
        print content
        
