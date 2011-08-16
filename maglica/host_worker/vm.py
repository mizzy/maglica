import subprocess
import socket

def create(args):
    image = args["image"]
    hostname = args["hostname"]
    
    cmdline = [
        "virt-clone",
        "-o",
        image,
        "-n",
        hostname,
        "-f",
        "/var/lib/libvirt/images/" + hostname + ".img",
        ]
    subprocess.call(cmdline)

    return "Created " + hostname + " successfully on " + socket.gethostname()
