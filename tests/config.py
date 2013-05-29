# $ nosetests -v --rednose --with-coverage tests/config.py

from nose.tools import *
import maglica.config


def test_config_load():
    config = maglica.config.load('etc/maglica.conf.example')
    eq_(config.hosts[0], "host0.example.com")
    eq_(config.hosts[1], "host1.example.com")
    eq_(config.client["host"], "client.example.com")
    eq_(config.client["pub_port"], 5555)
    eq_(config.client["rep_port"], 5556)

if __name__ == "__main__":
    test_config_load()
