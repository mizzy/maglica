# $ nosetests -v --rednose --with-coverage tests/util.py

from nose.tools import *
from maglica.util import *


def check_args_ok_test():
    args = {
        "image": "foo",
        "hostname": "bar",
    }
    options = {
        "mandatory": ["image", "hostname"],
        "optional": [],
    }
    ok_(check_args(args, options))


@raises(MaglicaCliException)
def check_args_except_test():
    args = {
        "hostname": "foo",
    }
    options = {
        "mandatory": ["image", "hostname"],
        "optional": [],
    }
    check_args(args, options)
