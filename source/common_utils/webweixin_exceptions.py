# coding: utf-8
"""
WebWeixin class raised exceptions
"""
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class OfflineException(Exception):
    """
    All exceptions that causing a WebWeixin instance go offline should inherit this class.
    """

    def __init__(self, offline_reason_db, message):
        """

        :param offline_reason_db: will write as 'latest_down_reason' in db later.
        :param message: Exception.message
        """
        super(OfflineException, self).__init__(message)
        self.offline_reason_db = offline_reason_db


class UinMisMatchException(OfflineException):
    def __init__(self, given_uin=0, actual_uin=0):
        """
        Exception caused by called PUT /wx/webot/{webotid} and set configStatus to true
        but {webotid}'s uin mismatched with the account's uin who scanned the QR code
        :param given_uin: specified uin by front
        :param actual_uin: the account's uin who scanned the QR code
        """
        super(UinMisMatchException, self).__init__(
            'Uin Mismatch',
            'Put online failed due to Uin mismatch(' +
            'restrict={uin}, scanner={uin_scanner}). '.format(uin=given_uin,
                                                              uin_scanner=actual_uin) +
            'Maybe try putting account A online but use account B to scan qr code?')
        self.given_uin = given_uin
        self.actual_uin = actual_uin


class PhoneLogoutException(OfflineException):
    def __init__(self):
        super(PhoneLogoutException, self).__init__(
            'PhoneLogout',
            '在手机上登出了微信')


class PhoneExitException(OfflineException):
    def __init__(self):
        super(PhoneExitException, self).__init__(
            'PhoneExit',
            '在手机上主动退出了')


class AnotherLoginException(OfflineException):
    def __init__(self):
        super(AnotherLoginException, self).__init__(
            'AnotherLogin',
            '在其他地方登录了 WEB 版微信')


class SyncCheckException(OfflineException):
    def __init__(self):
        super(SyncCheckException, self).__init__(
            'Internal Error',
            'synccheck 异常')


class RetCodeUnknownException(OfflineException):
    def __init__(self, ret_code=-1, selector=-1):
        super(RetCodeUnknownException, self).__init__(
            'Internal Error',
            '未知的 retcode: %s, selector: %s' % (ret_code, selector))
        self.ret_code = ret_code
        self.selector = selector


class WeChatLoginException(Exception):
    def __init__(self, msg):
        super(WeChatLoginException, self).__init__(msg)


class WeChatOnlineException(Exception):
    def __init__(self, msg):
        super(WeChatOnlineException, self).__init__(msg)

def _test():
    logging.info('Exceptions test.')
    exceptions = [UinMisMatchException, PhoneExitException, PhoneLogoutException,
                  AnotherLoginException, SyncCheckException, RetCodeUnknownException]
    for i, exception in enumerate(exceptions):
        try:
            raise exception
        except OfflineException as e:
            logging.info('Catch exception %d: %s' % (i, e.__class__.__name__))
            logging.info('Exception message: %s' % e.message)
            logging.info('Exception db reason: %s' % e.offline_reason_db)
        finally:
            pass
    return


if __name__ == '__main__':
    _test()
