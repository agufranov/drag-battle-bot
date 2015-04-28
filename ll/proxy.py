import time
import requests
import json


class Proxy:

    url = 'http://37.200.64.170/req.exe'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0',
        'Referer': 'http://static2.dragbattle.ru/wp_vk/WebPlayer/WebPlayer.unity3d?revision=579',
        'Connection': 'keep-alive'
    }
    proxies = {
        #'http': '127.0.0.1:8888'
    }
    aid = '2494274'

    def __init__(self, uid, hash, hash_off, code):
        self.uid, self.hash, self.hash_off, self.code = uid, hash, hash_off, code
        self.uniq = 0

    def request(self, req, params={}, json_object_pairs_hook=None):
        params['req'] = req
        params['hsh'] = self.hash
        params['hsh_off'] = self.hash_off
        params['code'] = self.code
        params['uniq'] = self.uniq
        while 1:
            try:
                response = requests.get(Proxy.url, params=params, headers=Proxy.headers, proxies=Proxy.proxies)
                self.uniq += 1
                return json.loads(response.text, object_pairs_hook=json_object_pairs_hook)
            except ValueError as e:
                print 'No JSON data in response:\n%s' % response.text
                time.sleep(10)
            except Exception as e:
                print 'Exception:', e.message
                time.sleep(10)


    @staticmethod
    def get_proxy(uid, auth):
        response = requests.get(Proxy.url, params={'req': 50, 'uid': uid, 'aid': Proxy.aid, 'auth': auth}, headers=Proxy.headers, proxies=Proxy.proxies).json()
        return Proxy(uid, response['h'], response['o'], response['c'])


if __name__ == '__main__':
    uid = '190625071'
    aid = '2494274'
    auth = '5a726748e7aceed37aef6e960373756d'
    proxy = Proxy.get_proxy(uid, aid, auth)
    print proxy.request(10)
    print proxy.request(10)
