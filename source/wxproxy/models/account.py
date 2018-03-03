# coding: utf-8
import json


class AccountObject():

    def __init__(self, tai_id, account_id, nick_name, cookies, uin, name, host, login_info, head_img,
                 latest_down_reason):
        self.tai_id = tai_id
        self.account_id = account_id
        self.nick_name = nick_name;
        self.cookies = cookies
        self.uin = uin
        self.name = name
        self.host = host
        self.login_info = login_info
        self.head_img = head_img
        self.latest_down_reason = latest_down_reason
        # """
        if isinstance(self.login_info, dict):
            self.login_info = json.dumps(self.login_info)
        if isinstance(self.cookies, dict):
            self.cookies = json.dumps(self.cookies)
        # """
