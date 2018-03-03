# coding: utf-8
import time
import logging
import qrcode

def get_r():
    return int(time.time() * 1000)


def get_js_r():
    # "rr": -541295957 ~new Date
    t = int(time.time() * 1000)
    return ~t + 1477468749823 + 1


def singleton(cls):
    instance = cls()
    instance.__call__ = lambda: instance
    return instance


def catchKeyboardInterrupt(fn):
    def wrapper(*args):
        try:
            return fn(*args)
        except KeyboardInterrupt:
            logging.info('[*] 强制退出程序')

    return wrapper


def str2qr(str_data):
    qr = qrcode.QRCode()
    qr.border = 1
    qr.add_data(str_data)
    qr.make()

    # qr.print_tty() or qr.print_ascii()
    # qr.print_ascii(invert=True)

    def print_QR(mat):
        for i in mat:
            black = '\033[40m  \033[0m'
            white = '\033[47m  \033[0m'
            print(''.join([black if j else white for j in i]))

    mat = qr.get_matrix()
    # code change by zwj
    # 此处代码在win10系统下会抛出IOError
    try:
        print_QR(mat)
    except IOError:
        print('print QR code error ...')