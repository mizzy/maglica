import subprocess
import socket
import guestfs
import re

def clone(args):
    image      = args["image"]
    hostname   = args["hostname"]
    image_file = "/var/lib/libvirt/images/" + hostname + ".img"
    cmdline = [
        "virt-clone",
        "-o",
        image,
        "-n",
        hostname,
        "-f",
        image_file,
        ]
    subprocess.call(cmdline)

    g = guestfs.GuestFS()
    g.add_drive('/var/lib/libvirt/images/' + hostname + '.img')
    g.launch()
    filesystems = g.list_filesystems()
    for filesystem in filesystems:
        if re.match(r'.+root$', filesystem[0]) or re.match(r'.+LogVol00$', filesystem[0]):
            fs = filesystem[0]

    g.mount(fs, '/')

    ifcfg='''DEVICE=%s
BOOTPROTO=dhcp
ONBOOT=yes
TYPE="Ethernet"
DHCP_HOSTNAME=%s
'''

    network='''NETWORKING=yes
HOSTNAME=%s
'''

    ifcfg0  = ifcfg % ('eth0', hostname)
    network = network % ( hostname )

    g.write_file('/etc/sysconfig/network-scripts/ifcfg-eth0', ifcfg0, 0)
    g.write_file('/etc/sysconfig/network', network, 0)
    g.write_file('/etc/udev/rules.d/70-persistent-net.rules', '', 0)
    g.sync()
    g.umount_all()

    return "Created " + hostname + " successfully on " + socket.gethostname()
