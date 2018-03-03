# coding: utf-8
import copy

def struct_friend_info(knownInfo):
    friendInfoTemplate = {}
    for k in ('UserName', 'City', 'DisplayName', 'PYQuanPin',
              'RemarkPYInitial', 'Province', 'KeyWord', 'RemarkName',
              'PYInitial', 'EncryChatRoomId', 'Alias', 'Signature', 'NickName',
              'RemarkPYQuanPin', 'HeadImgUrl'):
        friendInfoTemplate[k] = ''
    for k in ('UniFriend', 'Sex', 'AppAccountFlag', 'VerifyFlag', 'ChatRoomId',
              'HideInputBarFlag', 'AttrStatus', 'SnsFlag', 'MemberCount',
              'OwnerUin', 'ContactFlag', 'Uin', 'StarFriend', 'Statues'):
        friendInfoTemplate[k] = 0
    friendInfoTemplate['MemberList'] = []

    member = copy.deepcopy(friendInfoTemplate)
    for k, v in copy.deepcopy(knownInfo).items():
        member[k] = v
    return member
