import json
import inspect
import requests

import testAuth

urlAuth = 'http://172.17.0.2:5000/'
urlMsg = 'http://172.17.0.3:4000/'

def basic_test():
    try:
        testAuth.register_test('user1', 'password1')
    except AssertionError as e:
        # user already exists
        ...
    try:
        testAuth.register_test('user2', 'password2')
    except AssertionError as e:
        # user already exists
        ...

    token = testAuth.authenticate_test('user1', 'user2')
    data = {'sender': 'user1',
            'receiver': 'user2',
            'hash': token,
            'message': 'msg'
            }

    req = requests.post(urlMsg + 'message', data=json.dumps(data))
    assert req.status_code == 200, 'send message return error status'

    headers = {'Content-Type': 'application/json',
               'Authorization': token}
    req = requests.post(urlMsg + 'messages/user1', data=json.dumps(data), headers=headers)
    assert req.status_code == 200, 'server returned non ok status code'
    req = requests.post(urlMsg + 'messages/user2', data=json.dumps(data), headers=headers)
    assert req.status_code != 200, 'server returned sensitive data'


if __name__ == '__main__':
    tests = [test for key, test in globals().items() if
             (inspect.isfunction(test) or inspect.ismethod(test)) and 'test' in key]
    rval = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            rval = 1
            print(e, test, 'failed')
    print('all tests passed') if rval == 0 else print('Tests failed')
    exit(rval)