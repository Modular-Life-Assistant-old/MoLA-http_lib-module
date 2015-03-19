from core import Log
from core.decorator import async

from circuits import Component
import json
import os
import time
import urllib
import urllib.request


class Module(Component):
    timeout = 5

    @async
    def get(self, url, **kwargs):
        return self.get_sync(url, **kwargs)

    @async
    def get_json(self, url, **kwargs):
        return self.__json('get_sync', url, **kwargs)

    def get_sync(self, url, **kwargs):
        return self.__call('get', url, **kwargs)

    @async
    def head(self, url, **kwargs):
        return self.head_sync(url, **kwargs)

    @async
    def head_json(self, url, **kwargs):
        return self.__json('head_sync', url, **kwargs)

    def head_sync(self, url, **kwargs):
        return self.__call('head', url, **kwargs)

    @async
    def post(self, url, data, **kwarg):
        return self.post_sync(url, data, **kwarg)

    @async
    def post_json(self, url, data, **kwarg):
        return self.__json('post_sync', url, data, **kwarg)

    def post_sync(self, url, data, **kwargs):
        return self.__call('post', url, data=data, **kwargs)

    @async
    def put(self, url, data, **kwargs):
        return self.put_sync(url, data, **kwargs)

    @async
    def put_json(self, url, data, **kwargs):
        return self.__json('put_sync', url, data, **kwargs)

    def put_sync(self, url, data, **kwargs):
        return self.__call('put', url, data=data, **kwargs)

    def __call(self, method, url, data=None, **kwargs):
        if 'page' in kwargs:
            url = '%s/%s' (url, kwargs['page'])

        if data:
            encoded_data = urllib.parse.urlencode(data).encode('ascii')

        request = urllib.request.Request(url, encoded_data)
        request.get_method = lambda: method.upper()

        # set headers
        headers = kwargs.get('headers', {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
            'Referer': url,
        })

        for header in headers:
            request.add_header(header, headers[header])

        Log.debug('http_lib : %s %s' % (method, url))
        start = time.time()

        try:
            timeout = kwargs.get('timeout', self.timeout)
            response = urllib.request.urlopen(request, timeout=timeout)

            end = time.time()
            http_code = response.status
            headers = dict(response.getheaders())

            if 'download_path' in kwargs:
                html = ''
                dir_path = os.path.dirname(kwargs['download_path'])

                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)

                with open(kwargs['download_path'], 'wb') as f:
                    f.write(response.read())

            else:
                html = response.read().decode('utf8')

        except urllib.error.HTTPError as e:
            end = time.time()
            html = e.reason
            http_code = e.getcode()
            headers = {}

        except urllib.error.URLError as e:
            if kwargs.get('retry', 0) > 0:
                if 'retry_delay' not in kwargs:
                    kwargs['retry_delay'] = 2

                time.sleep(kwargs['retry_delay'])
                kwargs['retry_delay'] *= 2
                kwargs['retry'] -= 1

                return self.__call(method, url, data=data, **kwargs)
            raise e

        return {
            'response_time': end - start,
            'html': html,
            'code': http_code,
            'headers': headers,
        }

    def __json(self, method, *args, **kwargs):
        try:
            result = getattr(self, method)(*args, **kwargs)
            return json.loads(result['html'])

        except (TypeError, ValueError) as e:  # not json result
            return {
                'error': str(e),
                'result': result,
            }
