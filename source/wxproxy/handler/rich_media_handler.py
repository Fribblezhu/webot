# -*- coding: utf-8 -*-
# flake8: noqa

from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import unittest
import httplib
import os
import uuid

QINIU_ACCESS_KEY = 'TTZwPTRVcSVxibZHx3IgP448aqt2XBHRa8Qmo_hY'
QINIU_SECRET_KEY = '7bGHUQ2d2udLsRoyT9y4FaiCzU88O8R11-IJV2wq'
QINIU_BUCKET_NAME = 'test'
UPLOAD_API_HOST = 'localhost'
AUTO_DELETE = False


class RichMediaHandler:
    @classmethod
    def __dicret_qiniu_upload(cls, local_file, remote_file, bucket_name=QINIU_BUCKET_NAME):
        # import qiniu.config
        access_key = QINIU_ACCESS_KEY
        secret_key = QINIU_SECRET_KEY
        # 构建鉴权对象
        q = Auth(access_key, secret_key)
        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name, remote_file, 3600)
        ret, info = put_file(token, remote_file, local_file)
        print(info)
        assert ret['key'] == remote_file
        assert ret['hash'] == etag(local_file)
        return

    @classmethod
    def upload(cls, local_file, remote_file='', bucket_name=QINIU_BUCKET_NAME):
        """
        class method upload. upload local file to qiniu and retrieves remote file url.
        :param local_file: related/absolute path of a local file
        :param remote_file: specified remote file name
        :param bucket_name: qiniu bucket name, default=QINIU_BUCKET_NAME
        :return: remote file url, is_upload_success(boolean)
        """
        if remote_file == '':
            remote_file = cls.__gen_uuid()
        local_file = cls.__get_abs_path(local_file)
        url = "/v1/qiniu/upload?key=%s&localFile=%s&token=root-weimiyun-9@usstpwd!" % (remote_file, local_file)
        try:
            conn = httplib.HTTPConnection(UPLOAD_API_HOST)
            conn.request(method="POST", url=url)
            response = conn.getresponse()
            res = response.read()
            if AUTO_DELETE:
                os.remove(local_file)
            return res, True
        except Exception, e:
            return 'Connection refused', False

    @classmethod
    def __get_abs_path(cls, file):
        return os.path.abspath(file)

    @classmethod
    def __gen_uuid(cls):
        return uuid.uuid1()


class RichMediaHandlerTest(unittest.TestCase):
    def test_upload(self):
        RichMediaHandler.upload(local_file='./test.txt', remote_file='test.txt')


if __name__ == '__main__':
    unittest.main()
