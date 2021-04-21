#import pytest
#from pytask import task
#import time
#import threading
#
#def test_basic():
#    values = []
#    def call_something():
#        time.sleep(2)
#        return "the result (can be any objects)"
#    def receive_the_response(datas):
#        values.append(datas)
#        return ['ok', 'not ok']
#    def finaly_do_this(datas):
#        values.append(datas)
#
#    #Run tasks asynchrnously
#    mytask = task(lambda datas: call_something()
#    ).then(lambda datas: receive_the_response(datas)
#    ).then(lambda datas: finaly_do_this(datas))
#    mytask.wait()
#    assert values[0] is "the result (can be any objects)"
#    assert values[1][0] is "ok"
#    assert values[1][1] is "not ok"
#    assert threading.active_count() is 1
#