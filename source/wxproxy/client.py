# coding: utf-8
from __future__ import absolute_import
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if not sys.path.__contains__(parent_dir):
    sys.path.insert(0, parent_dir)

from common_utils.log import init_logging
from common_utils.webweixin_exceptions import OfflineException, WeChatLoginException, WeChatOnlineException
from wxproxy.wechat import WebWeChat

logger = init_logging('client')


def main(tai_id=0,
         uin=None,
         name=None,
         status_obj=None,
         **kwargs):
    __wechat = WebWeChat(tai_id, uin, name, status_obj,  **kwargs)

    try:
        if uin:
            # todo re_login or login
            pass
        else:
            try:
                __wechat.login()
                __wechat.online()
                __wechat.running()
            except WeChatLoginException as e:
                logger.error('login failed... msg: %s' % e)
            except WeChatOnlineException as e:
                logger.error('online failed... msg: %s' % e)

        meta = {'status': 'SUCCESS', 'message': '任务完成'}

    except OfflineException as offline_exception:
        logger.info('强制退出程序')
        logger.info('{ex.message}'.format(ex=offline_exception))
        __down_reason = offline_exception.offline_reason_db
        meta = {'status': 'FAILURE', 'message': '强制退出程序'}
    except KeyboardInterrupt:
        logger.warning('强制退出程序')
        __down_reason = 'Interrupted by console (DEBUG)'
        meta = {'status': 'FAILURE', 'message': '强制退出程序'}
    except Exception as e:
        import traceback
        logger.error('%s' % traceback.format_exc())
        logger.warning('异常退出程序')
        __down_reason = 'Internal Error'
        meta = {'status': 'FAILURE', 'message': str(e)}


if __name__ == '__main__':
    # python client.py --uin 37471765
    # python client.py --uin 37471765 -n gnocob
    # python client.py --uin 37471765 -r 120.55.70.1
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-u', '--uin', help='wechat uin', type=int)
    parser.add_argument(
        '-n', '--name', help='unique client name yourself', default='')
    parser.add_argument(
        '-q', '--qname', help='rq queue name', default='default')
    parser.add_argument(
        '-k', '--kwargs', help='additional keyword args', default='{}')

    args = parser.parse_args()
    logger.debug(args)
    kw = eval(args.kwargs)

    main(0, args.uin, args.name, None, **kw)
