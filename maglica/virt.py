import libvirt
import maglica.config
from xml.etree.ElementTree import *
import subprocess


class Virt:

    def __init__(self, hosts=[{"name": "test", "weight": 1}]):
        self.hosts = []
        self.conf = {}
        for host in hosts:
            if host["name"] == "test":
                uri = "test:///default"
            else:
                uri = self.uri(host["name"])
            conn = libvirt.open(uri)
            weight = 1
            if "weight" in host:
                weight = host["weight"]
            self.hosts.append({"name": host[
                              "name"], "conn": conn, "weight": host["weight"]})

    def get_active_domains(self):
        vms = []
        for host in self.hosts:
            conn = host["conn"]
            ids = conn.listDomainsID()
            for id in ids:
                dom = conn.lookupByID(id)
                vms.append({
                    "name": dom.name(),
                    "state": "running",
                    "host": host["name"],
                })

        return vms

    def get_active_domains_of(self, host):
        domains = self.get_active_domains()
        vms = []
        for domain in domains:
            if domain["host"] == host:
                vms.append(domain)
        return vms

    def get_inactive_domains(self):
        vms = []
        for host in self.hosts:
            conn = host["conn"]
            domains = conn.listDefinedDomains()
            for domain in domains:
                vms.append({
                    "name": domain,
                    "state": "shut off",
                    "host": host["name"],
                })

        return vms

    def get_active_domain(self, name):
        for host in self.hosts:
            conn = host["conn"]
            ids = conn.listDomainsID()
            for id in ids:
                dom = conn.lookupByID(id)
                if name == dom.name():
                    return (dom, host["name"])
        return (None, None)

    def get_inactive_domain(self, name):
        domains = self.get_inactive_domains()
        for domain in domains:
            if name == domain["name"]:
                return domain

    def get_domains(self):
        domains = self.get_active_domains()
        for domain in self.get_inactive_domains():
            domains.append(domain)

        return domains

    def start(self, name):
        dom = self.get_inactive_domain(name)
        if not dom:
            raise Exception("%s not found or already started." % name)

        for host in self.hosts:
            if host["name"] == dom["host"]:
                dom = host["conn"].lookupByName(name)
                return dom.create()

    def stop(self, name):
        (dom, host) = self.get_active_domain(name)
        if not dom:
            raise Exception("%s not found or already stopped." % name)

        return dom.shutdown()

    def destroy(self, name):
        (dom, host) = self.get_active_domain(name)
        if not dom:
            raise Exception("%s not found or already stopped." % name)

        return dom.destroy()

    def attach_iso(self, name, iso):
        (dom, host) = self.get_active_domain(name)
        if not dom:
            dom = self.get_inactive_domain(name)
            host = dom["host"]

        for x in self.hosts:
            if host == x["name"]:
                conn = x["conn"]

        dom = conn.lookupByName(name)

        cdrom = None
        desc = fromstring(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
        for disk in desc.findall(".//disk"):
            if disk.get("device") == "cdrom":
                cdrom = disk
                if cdrom.find(".//source"):
                    cdrom.find(".//source").set("file", iso)
                else:
                    desc.find(".//devices").remove(cdrom)
                    cdrom = None

        if not cdrom:
            xml = """
<disk type="file" device="cdrom">
  <driver name="qemu"/>
  <source file="%s" />
  <target dev="hdc" bus="ide"/>
  <readonly/>
</disk>
   """
        xml = xml % (iso)
        desc.find(".//devices").insert(-1, fromstring(xml))
        conn.defineXML(tostring(desc))
        return True

    def set_boot_device(self, name, dev):
        (dom, host) = self.get_active_domain(name)
        if not dom:
            dom = self.get_inactive_domain(name)
            host = dom["host"]

        for x in self.hosts:
            if host == x["name"]:
                conn = x["conn"]

        dom = conn.lookupByName(name)

        desc = fromstring(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
        desc.find(".//boot").set("dev", dev)

        conn.defineXML(tostring(desc))
        return True

    def set_vcpus(self, name, vcpus):
        (dom, host) = self.get_active_domain(name)
        if not dom:
            dom = self.get_inactive_domain(name)
            host = dom["host"]

        for x in self.hosts:
            if host == x["name"]:
                conn = x["conn"]

        dom = conn.lookupByName(name)

        desc = fromstring(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
        desc.find(".//vcpu").text = vcpus
        conn.defineXML(tostring(desc))

        if dom.isActive():
            dom.setVcpus(int(vcpus))

        return True

    def set_memory(self, name, size):
        (dom, host) = self.get_active_domain(name)
        if not dom:
            dom = self.get_inactive_domain(name)
            host = dom["host"]

        for x in self.hosts:
            if host == x["name"]:
                conn = x["conn"]

        dom = conn.lookupByName(name)

        desc = fromstring(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
        desc.find(".//memory").text = str(size)
        desc.find(".//currentMemory").text = str(size)
        conn.defineXML(tostring(desc))

        if dom.isActive():
            dom.setMemory(int(size))

        return True

    def info(self, name):
        (dom, host) = self.get_active_domain(name)
        cmdline = ["virsh", "--connect", self.uri(host), "vncdisplay", name]
        p = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
        out = p.stdout.readline().rstrip()
        return {
            "name": name,
            "host": host,
            "vncport": 5900 + int(out.replace(":", ""))
        }

    def console(self, name):
        (dom, host) = self.get_active_domain(name)
        subprocess.call(["virsh", "--connect", self.uri(
            host), "console", name])

    def uri(self, host):
        if not self.conf:
            self.conf = maglica.config.load()

        if not hasattr(self.conf, "libvirt"):
            return "remote://%s/" % host

        libvirt = self.conf.libvirt
        return "%s+%s://%s/%s" % (
            libvirt["driver"], libvirt["transport"], host, libvirt["path"]
        )
