import json
import inspect
import requests

url = 'http://172.17.0.2:5000/'

def pass_test():
    return True


def register_test(username='value1', password='value2'):
    data = {
        'username': username,
        'password': password
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url+'register', data=json.dumps(data), headers=headers)
    unregister_test(username, password)
    response = requests.post(url + 'register', data=json.dumps(data), headers=headers)
    assert response.status_code == 201

    response = requests.post(url+'register', data=json.dumps(data), headers=headers)
    assert response.status_code == 401

def unregister_test(username='value1', password='value2'):
    data = {
        'username': username,
        'password': password
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url+'unregister', data=json.dumps(data), headers=headers)
    assert response.status_code == 200


def authenticate_test(username='value1', password='value2'):
    data = {
        'username': username,
        'password': password
    }
    headers = {
        'Content-Type': 'application/json'
    }
    requests.post(url+'register', data=json.dumps(data), headers=headers)

    response = requests.post(url+'auth', data=json.dumps(data), headers=headers)
    assert response.status_code == 201
    return response.json()['token']

def verify_test():
    token = authenticate_test()
    data = {
        'id': 'value1',
        'cookie': token
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url+'verif', data=json.dumps(data), headers=headers)
    assert response.status_code == 201

    data = {
        'id': 'value1',
        'cookie': 'abcdefghijklmnopqrst'
    }
    response = requests.post(url + 'verif', data=json.dumps(data), headers=headers)
    assert response.status_code != 201

if __name__ == '__main__':
    tests = [ test for key, test in globals().items() if (inspect.isfunction(test) or inspect.ismethod(test)) and 'test' in key ]
    rval = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            rval = 1
            print(e, test, 'failed')
    print('all tests passed') if rval == 0 else print('Tests failed')
    exit(rval)