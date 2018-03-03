# coding: utf-8
import requests
import json

import xmltodict as xmltodict
from wxproxy.wx_apis.send import webwxsendmsg
from common_utils.log import init_logging
from common_utils.emoji import emoji_formatter
import re
import time
import html
from collections import defaultdict

logger = init_logging('msg')



def handle_msg(account, tai, r):

    # 发红包/领取红包时所有都为空
    if not (r['AddMsgList'] or r['DelContactList'] or
            r['ModChatRoomMemberList'] or r['ModContactList']):
        logger.warning('同步消息为空，可能在手机上收发了红包，或消息已同步')
    elif r['ModChatRoomMemberList']:
        logger.warning('发现 ModChatRoomMemberList: %s' % json.dumps(r))

    for contact in r['DelContactList']:
        logger.warning('[*] 删除联系人: %s' % contact['UserName'])

    for contact in r['ModContactList']:
        contact['tai'] = tai
        if contact['UserName'][:2] == '@@':
            logger.info('[*] 更新群: %s' % contact['UserName'])
        else:
            logger.info('[*] 更新联系人: %s' % contact['NickName'])
    for msg in r['AddMsgList']:
        if msg['MsgType'] != 51:
            logger.info('msg: %s' % msg)
        parse_msg(account, msg)


def parse_msg(account, msg):
    msgType = msg['MsgType']
    content = emoji_formatter(msg['Content'])
    content = html.unescape(content)
    message = None

    if msgType == 1:
        pass
    elif msgType == 3:  # img
        # todo
        logger.info('get a image message ...')
    elif msgType == 34:  # voice
        # todo
        logger.info('get a voice message ...')
    elif msgType == 37:  # friends
        message = '%s请求添加好友: %s' % (msg['RecommendInfo']['NickName'],
                                    msg['RecommendInfo']['Content'])
        kwargs = {
            'status': msg['Status'],
            'userName': msg['RecommendInfo']['UserName'],
            'ticket': msg['Ticket'],
            'userInfo': msg['RecommendInfo'],
        }
        # todo 同意好友请求
    elif msgType == 42:  # name card
        info = msg['RecommendInfo']
        message = '\n'.join([
            '发送了一张名片:', '=========================',
            '= 昵称: %s' % info['NickName'], '= 微信号: %s' % info['Alias'],
            '= 地区: %s %s' % (info['Province'], info['City']), '= 性别: %s' %
            ['未知', '男', '女'][info['Sex']], '========================='
        ])
    elif msgType == 43:  # video
        message = '发了一个视频，请在手机上查看'
    elif msgType == 47:  # 动画表情
        url = _searchContent('cdnurl', content)
        if url:
            message = '发了一个动画表情，点击下面链接查看: %s' % url
        else:
            message = '发了一个动画表情，请在手机上查看'
    elif msgType == 49:  # file
        if msg['AppMsgType'] == 6:
            # TODO 参考itchat 下载文件
            message = '发了一个文件: %s' % msg['FileName']
        else:
            # TODO itchat 上有解析17、2000，暂不知道是什么
            appMsgType = defaultdict(lambda: "")
            appMsgType.update({3: '音乐', 5: '链接', 7: '微博'})
            message = '\n'.join([
                '分享了一个%s:' % appMsgType[msg['AppMsgType']],
                '=========================', '= 标题: %s' % msg['FileName'],
                '= 描述: %s' % _searchContent('des', content, 'xml'),
                '= 链接: %s' % msg['Url'], '= 来自: %s' % _searchContent(
                    'appname', content, 'xml'), '========================='
            ])
    elif msgType == 51:  # phone init
        # todo  op = 2 进入聊天, op = 5 离开聊天, op = 4 未读消息, op = 9 刷新朋友圈
        pass
    elif msgType == 62:  # small video
        message = '发了一段小视频: '
    elif msgType == 10002:
        message = _searchContent('replacemsg', content, 'xml')
    elif msgType == 10000:
        # todo 红包
        pass
    else:
        message = '[*] 不支持的消息类型，请在手机上查看'
        logger.warning(json.dumps(msg))

    sender_id = msg['FromUserName']
    receiver_id = msg['ToUserName']

    # 收到群消息，解析出发送者
    """
    if msg['FromUserName'][:2] == '@@':
        group_id = sender_id

        r = re.match('(@[0-9a-z]*?):<br/>(.*)$', content)
        if r:
            sender_id, content = r.groups()
        receiver_id = group_id
    content = message if message else content.replace('<br/>', '\n')
    """
    if sender_id == 'newsapp':
        content = 'message from newsapp'

    if msg['MsgType'] == 51:
        try:
            d = xmltodict.parse(content)
            op = int(d['msg']['op']['@id'])
        except Exception as e:
            if e.__class__.__name__ == 'ExpatError':
                logger.warning('Caught error {e.__class__}: {e.message}'.format(e=e))
                logger.warning('Assuming phone entering chat UI')
            op = 0

        if op == 1:
            content = '[*] 当前聊天界面有新的消息'
        elif op == 2:
            content = '[*] 进入聊天界面'
        elif op == 5:
            content = '[*] 离开聊天界面'
        elif op == 4:
            content = '[*] 有未读消息'
        elif op == 7:
            content = '[*] 朋友圈动态已读'
        elif op == 9:
            content = '[*] 朋友圈刷新'

        if int(op) in (1, 2, 5):
            username = d['msg']['op']['username']

    date = time.strftime('%Y-%m-%d %H:%M:%S',
                         time.localtime(msg['CreateTime']))
    logger.info('%s %s -> %s: %s' % (date, sender_id, receiver_id, content))
    webwxsendmsg(account, '别说话下班了...', sender_id)
    return


def _searchContent(key, content, fmat='attr'):
    if fmat == 'attr':
        pm = re.search(key + '\s?=\s?"([^"<]+)"', content)
        if pm:
            return pm.group(1)
    elif fmat == 'xml':
        pm = re.search('<{0}>([^<]+)</{0}>'.format(key), content)
        if not pm:
            pm = re.search('<{0}><\!\[CDATA\[(.*?)\]\]></{0}>'.format(key),
                           content)
        if pm:
            return pm.group(1)
    return ''
