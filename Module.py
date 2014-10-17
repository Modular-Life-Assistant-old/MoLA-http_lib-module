from core import Log

import time
import urllib
import urllib.request


class Module:
    def __init__(self):
        self.timeout = 5

    def get(self, url, **options):
        return self.__call('get', url, **options)

    def head(self, url, **options):
        return self.__call('head', url, **options)

    def post(self, url, data, **options):
        return self.__call('post', url, data=data, **options)

    def __call(self, method, url, data=None, **options):
        if 'page' in options:
            url = '%s/%s' (url, options['page'])

        if data:
            data = urllib.parse.urlencode(data).encode('ascii')

        request = urllib.request.Request(url, data)
        request.get_method = lambda : method.upper()
        request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')
        request.add_header('Referer', url)

        Log.debug('http_lib : %s %s' % (method, url))
        start = time.time()

        try:
            response = urllib.request.urlopen(request, timeout=self.timeout)
            
            end = time.time()
            html = response.read().decode('utf8')
            http_code = response.status

        except urllib.error.HTTPError as e:
            end = time.time()
            html = e.reason
            http_code = e.getcode()

        return {
            'response_time': end - start,
            'html': html,
            'code': http_code,
        }

