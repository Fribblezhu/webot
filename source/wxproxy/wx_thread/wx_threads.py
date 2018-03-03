# coding: utf-8
import threading
import time
from common_utils.log import init_logging

logger = init_logging('wx_thread')


class ContactImgUploadThread(threading.Thread):
    def __init__(self, i, contact, uploader, uuid_img_dict, uuid_contact_dict):
        threading.Thread.__init__(self)
        self.setName('contact_uploader_%s' % i)
        self.i = i
        self.contact = contact
        self.uploader = uploader
        self.uuid_img_dict = uuid_img_dict
        self.uuid_contact_dict = uuid_contact_dict

    def run(self):
        img_url = self.uploader.save_head_img(self.contact)
        self.uuid_contact_dict[self.i] = self.contact
        self.uuid_img_dict[self.i] = img_url


class GuardThread(threading.Thread):
    def __init__(self, wxobj):
        super(GuardThread, self).__init__()
        self.wxobj = wxobj
        self.setName('OfflineWatcher of {wxobj.uin}'.format(wxobj=wxobj))

    def run(self):
        logger.info('{thread.name} start running.'.format(thread=self))
        while not self.wxobj.exit_flag:
            time.sleep(5)
        return

