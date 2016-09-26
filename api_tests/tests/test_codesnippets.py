# pip install pytest requests
# py.test
import requests
import json


def test_post_snippet():
    url = 'http://127.0.0.1:8888/snippets/'
    snippet_data = {
        "style"   : "vom",
        "code"    : "console.log('hi')",
        "language": "js",
        "title"   : "test1",
        "linenos" : True,
    }
    data = snippet_data.copy()
    data["owner"] = 1
    resp = requests.post(
        url,
        json.dumps(data),
        headers={
            'Content-type': 'application/json',
        }
    )
    assert resp.status_code == 200
    assert all(item in resp.json().items() for item in snippet_data.items())

def test_get_all_snippets():
    url = 'http://127.0.0.1:8888/snippets/'
    resp = requests.get(url,
        headers={
            'Content-type': 'application/json',
        }
    )
    assert resp.status_code == 200
    assert type(resp.json()) == list


def test_get_one_snippet():
    url = 'http://127.0.0.1:8888/snippets/'
    resp_all = requests.get(url)
    if resp_all.status_code == 200:
        one_snippet = resp_all.json()[-1]
        resp_one = requests.get(
            one_snippet['url'],
            headers={
                'Content-type': 'application/json',
            }
        )
        assert one_snippet['id'] == resp_one.json()['id']


def test_put_snippet():
    data = {
        "style"   : "YYYYYey",
        "code"    : "console.log('hi')",
    }
    url = 'http://127.0.0.1:8888/snippets/'
    resp_all = requests.get(url)
    if resp_all.status_code == 200:
        one_snippet = resp_all.json()[-1]
        resp = requests.put(
            one_snippet['url'],
            json.dumps(data),
            headers={
                'Content-type': 'application/json',
            }
        )
        assert resp.status_code == 200
        assert all(item in resp.json().items() for item in data.items())


def test_delete_snippet():
    url = 'http://127.0.0.1:8888/snippets/'
    resp_all = requests.get(url)
    if resp_all.status_code == 200:
        one_snippet = resp_all.json()[-1]
        resp = requests.delete(one_snippet['url'])
        assert resp.status_code == 200
