# $ nosetests -v --rednose --with-coverage tests/virt.py

from nose.tools import *
from maglica.virt import Virt 
import maglica.config

xml = '''
<domain type='test'>
  <name>test2</name>
  <memory>8388608</memory>
  <currentMemory>2097152</currentMemory>
  <vcpu>2</vcpu>
  <os>
    <type arch='i686'>hvm</type>
    <boot dev='hd'/>
  </os>
  <clock offset='utc'/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>destroy</on_crash>
  <devices>
  </devices>
</domain>
'''

def test_get_active_domains():
    virt = Virt()
    dom = virt.get_active_domains()[0]
    eq_(dom["name"], "test")
    eq_(dom["host"], "test")
    eq_(dom["state"], "running")

def test_get_inactive_domains():
    virt = Virt()
    virt.hosts[0]["conn"].defineXML(xml)
    dom = virt.get_inactive_domains()[0]
    eq_(dom["name"], "test2")
    eq_(dom["host"], "test")
    eq_(dom["state"], "shut off")

def test_get_active_domain():
    virt = Virt()
    (dom, host) = virt.get_active_domain("test")
    eq_(host, "test")
    eq_(dom.name(), "test")
    ok_(dom.isActive())

def test_get_inactive_domain():
    virt = Virt()
    virt.hosts[0]["conn"].defineXML(xml)
    dom = virt.get_inactive_domain("test2")
    eq_(dom["name"], "test2")
    eq_(dom["host"], "test")
    eq_(dom["state"], "shut off")

def test_get_domains():
    virt = Virt()
    virt.hosts[0]["conn"].defineXML(xml)
    dom = virt.get_inactive_domain("test2")
    domains = virt.get_domains()
    eq_(domains[0]["name"], "test")
    eq_(domains[1]["name"], "test2")

def test_start_and_stop():
    virt = Virt()
    eq_(virt.stop("test"), 0)
    eq_(virt.start("test"), 0)

@raises(Exception)
def test_already_started_exception():
    virt = Virt()
    virt.start("test")

@raises(Exception)
def test_start_not_exist_exception():
    virt = Virt()
    virt.start("not_exist")


@raises(Exception)
def test_already_stopped_exception():
    virt = Virt()
    virt.stop("test")
    virt.stop("test")

@raises(Exception)
def test_stop_not_exist_exception():
    virt = Virt()
    virt.stop("not_exist")

def test_attach_iso_to_active_domain():
    virt = Virt()
    ok_(virt.attach_iso("test", "test.iso"))

def test_set_boot_device():
    virt = Virt()
    ok_(virt.attach_iso("test", "cdrom"))

def test_set_vcpus():
    virt = Virt()
    ok_(virt.set_vcpus("test", "1"))

def test_set_memory():
    virt = Virt()
    ok_(virt.set_memory("test", 1024*1024))
    
def test_uri_default():
    virt = Virt()
    eq_(virt.uri("host0.example.jp"), "remote://host0.example.jp/")

def test_uri_qemu():
    virt = Virt()

    conf = maglica.config.load_from_dict({
        "libvirt": {
            "driver"    : "qemu",
            "transport" : "tcp",
            "path"      : "system",
        }
    })

    virt.conf = conf

    eq_(virt.uri("host0.example.jp"), "qemu+tcp://host0.example.jp/system")
