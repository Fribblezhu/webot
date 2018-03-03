from common_utils.http import _get
from wxproxy.handler.rich_media_handler import RichMediaHandler
import logging
import os
import re

# GET https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxgetheadimg?seq=0&username=@@72e80754f2ed520caee4fda2f5bb7728dc143d7256d84b366c7e58bbee071f23&skey=@crypt_70cf22a_7d37d7081b857ed5390a73dd26e924b4 HTTP/1.1
# Host: wx2.qq.com
# Connection: keep-alive
# User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36
# Accept: image/webp,image/*,*/*;q=0.8
# Referer: https://wx2.qq.com/
# Accept-Encoding: gzip, deflate, sdch, br
# Accept-Language: zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4
# Cookie: RK=ZDObIWQLe2; eas_sid=H194F9j0D3G6R2k217m1k4Y4p8; pgv_pvi=456282112; tvfe_boss_uuid=c5792d1e730b9478; webwxuvid=d1920c23ef23c0445189d2f620d8d407704648e91a2abaeb4e8fa98666091dac43d2e594e6f085447a9b7183de1f8995; pac_uid=1_765624429; ptcz=cf79a163b4dfd1fa8fdc92bcf80af96a56f51719fcb15029bbe3812742707c88; pt2gguin=o0765624429; pgv_pvid=9532689260; o_cookie=765624429; wxpluginkey=1492043941; pgv_si=s346575872; wxuin=2960450528; wxsid=xxoXbIVoxK+hl5V+; wxloadtime=1492090251; webwx_data_ticket=gSemrkryrHXzczCtqIWUuRK7; webwx_auth_ticket=CIsBENXUnNIOGoABCWpd5z6vraPXQmeEi104L8bFqm/xmelVJhoR7VPnzZ6H/LePmQdQUFAddzCEBujbwO/CPZr8kQ/ZqQ3F152q0oE3276E4ABmBO25WPvc4wBNnNmgWtx8u90Sm9Wd8ngrMc28v+BQpEq1vg2XVIERecxl6N9J25EJ89oyzDStwtY=; mm_lang=zh_CN; MM_WX_NOTIFY_STATE=1; MM_WX_SOUND_STATE=1
env_conf_dict = dict()

try:
    env_config = open('source/env.conf')
    lines = env_config.readlines()
    for line in lines:
        if line == '':
            continue
        sp = line.split('=')
        env_conf_dict[sp[0]] = sp[1]
    env_config.close()
except IOError:
    pass


def get_conf(conf_name, default):
    return env_conf_dict[conf_name] if conf_name in env_conf_dict else default


class HeadImgUploader:
    STRING_HEAD_IMG_KEY = 'HeadImgUrl'
    # STRING_HEAD_IMG_HOST = 'https://wx2.qq.com' # not in use
    STRING_NICK_NAME = 'NickName'
    STRING_ACCOUNT_ID = 'UserName'
    STRING_GROUP_ID = 'UserName'
    FAILED_BEHAVIOUR = get_conf('HeadImgUploader.FAILED_BEHAVIOUR', 'skip_download')

    def __init__(self):
        self.cookie = ''
        self.skip_uploading = False
        self.skip_downloading = False
        self.auto_delete = False

    def set_cookie(self, cookie):
        self.cookie = cookie

    def get_head_img_url(self, contact_dic, **kwargs):
        url = contact_dic[HeadImgUploader.STRING_HEAD_IMG_KEY]
        # if url.find('skey=@') == -1:
        #     url += kwargs['skey']
        # print(url)
        return url

    def save_head_img(self, contact_dic, **kwargs):
        if self.skip_downloading:
            return ''
        head_img_url = self.get_head_img_url(contact_dic, **kwargs)
        target_id = kwargs.get('username', contact_dic[HeadImgUploader.STRING_ACCOUNT_ID])
        if '@@' in target_id:
            target_id = target_id.replace('@@', 'G')
        else:
            target_id = target_id.replace('@', 'U')
        nick_name = contact_dic[HeadImgUploader.STRING_NICK_NAME]
        logging.info('%s -> %s' % (nick_name, target_id))
        pm = re.search(r'(https://\S+/)', head_img_url)
        if pm is None:
            logging.info('HeadImgUrl is empty, skip downloading.')
            return ''
        ref = pm.group(1)
        try:
            result = _get(head_img_url,
                          referer=ref,
                          accept='image/webp,image/*,*/*;q=0.8',
                          accept_encoding='gzip, deflate, sdch, br',
                          accept_language='zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4'
                          )
            if 'show_url' in kwargs:
                logging.warning('head img url is: %s' % head_img_url)
            file_stat = 0
            img_file = open('saved/%s.jpg' % target_id, 'wb')

            # do not change order!
            if not result:
                logging.warning('Wx head img get failed. Empty response.')
                return ''

            img_file.write(result)
            file_stat = 1

            img_file.close()
        finally:
            if file_stat == 1 and not self.skip_uploading:
                return self.upload_head_img(target_id)
            # if get img fail or upload fail, return '' to store in db
            return ''

    def upload_head_img(self, account_id):
        result, API_call_success = RichMediaHandler.upload('saved/%s.jpg' % account_id, account_id)
        if 'http://omwcdvt6n.bkt.clouddn.com/' in str(result):
            return result
        if self.auto_delete:
            os.remove('saved/%s.jpg' % account_id)
        upload_failed = result.find('error') or \
                        result.find('Connection refused')
        if upload_failed or (not API_call_success):
            logging.warning('qiniu upload API call result:')
            logging.warning(result)
            logging.warning('Upload img failed.')
            if HeadImgUploader.FAILED_BEHAVIOUR == 'skip_upload':
                logging.warning('Skip later uploads.')
                self.skip_uploading = True
            if HeadImgUploader.FAILED_BEHAVIOUR == 'skip_download':
                logging.warning('Skip later downloads.')
                self.skip_downloading = True
            return ''
            # if upload fail, return '' to store in db
        else:
            return result
