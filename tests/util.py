# $ nosetests -v --rednose --with-coverage tests/util.py

from nose.tools import *
import maglica.util

def check_args_ok_test():
    args = {
        "image"   : "foo",
        "hostname": "bar",
    }
    options = {
        "mandatory" : ["image", "hostname"],
        "optional"  : [],
    }
    ok_(maglica.util.check_args(args, options))
    
@raises(TypeError)
def check_args_except_test():
    args = {
        "hostname": "foo",
    }
    options = {
        "mandatory" : ["image", "hostname"],
        "optional"  : [],
    }
    maglica.util.check_args(args, options)
    
