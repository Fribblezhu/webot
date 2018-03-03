# coding: utf-8
import json
import logging
import ssl
from urllib import request, parse
from .control import retry

LOGGING_DEBUG = False


def logging_debug(msg):
    if LOGGING_DEBUG:
        logging.debug(msg)


# the http response result is a bytes object..
@retry(5)
def handle_request(_request, timeout=35):
    try:
        response = request.urlopen(_request, timeout=timeout)
        data = response.read()
    except request.HTTPError as e:
        logging.error('HTTPError = %s' % e.code)
        raise e
    except request.URLError as e:
        logging.error('URLError = %s' % e.reason)
        raise e
    except ssl.SSLError as e:
        logging.error('SSLError = %s' % str(e))
        raise e
    # except request.HTTPException as e:
    #    logging.error(e.__class__.__name__)
    #    raise e
    except Exception as e:
        import traceback
        logging.error('%s' % traceback.format_exc())
        raise e
    else:
        if not data:
            logging.error('返回为空，检查session/cookie 是否有效')
        return data


def get(url, api=None, referer='https://wx.qq.com/', accept='', accept_encoding='', accept_language=''):
    base_url = url.split('?')[0]
    logging_debug(base_url)

    _request = request.Request(url=url)
    _request.add_header('Referer', referer)
    if accept != '':
        _request.add_header('Accept', accept)
    if accept_encoding != '':
        _request.add_header('Accept-Encoding', accept_encoding)
    if accept_language != '':
        _request.add_header('Accept-Language', accept_language)
    if api == 'webwxgetvoice':
        _request.add_header('Range', 'bytes=0-')
    if api == 'webwxgetvideo':
        _request.add_header('Range', 'bytes=0-')
    logging_debug('headers:%s\ndata:%s' % (_request.headers, _request.data))
    try:
        return handle_request(_request)
    except Exception:
        return ''


def post(url, params, jsonfmt=True):
    base_url = url.split('?')[0]
    logging_debug(base_url)

    if jsonfmt:
        _request = request.Request(url=url, data=json.dumps(params).encode())
        _request.add_header('Content-Type', 'application/json; charset=UTF-8')
        # Content-Type!!!, not ContentType
    else:
        _request = request.Request(url=url, data=parse.urlencode(params).encode())

    try:
        data = handle_request(_request)

        if jsonfmt:
            return json.loads(data.decode('utf-8'), object_hook=decode_dict)
        return data
    except Exception:
        return ''


def decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, bytes):
            item = item.decode('utf-8')
        elif isinstance(item, list):
            item = decode_list(item)
        elif isinstance(item, dict):
            item = decode_dict(item)
        rv.append(item)
    return rv


def decode_dict(data):
    rv = {}
    for key, value in data.items():
        if isinstance(key, bytes):
            key = key.decode('utf-8')
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        elif isinstance(value, list):
            value = decode_list(value)
        elif isinstance(value, dict):
            value = decode_dict(value)
        rv[key] = value
    return rv


def get_base_request(**kwargs):
    return {
        'Uin': int(kwargs['uin']),
        'Sid': kwargs['sid'],
        'Skey': kwargs['skey'],
        'DeviceID': kwargs['deviceid']
    }
