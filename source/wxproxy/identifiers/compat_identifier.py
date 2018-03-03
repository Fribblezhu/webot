


class CompatIdentifier:
    """due to unsolved sqlalchemy problems, temporaly use this CompatIdentifier"""

    @classmethod
    def handle_new_account(cls, query_item, **kwargs_update_info):
        if query_item is None:
            kwargs_update_info['is_p2p_monitored'] = True
            new_account = add_account(**kwargs_update_info)
            return new_account
        else:
            query_item.update(**kwargs_update_info)
            return query_item

    @classmethod
    def find_old_account(cls, uin):
        return db.session.query(AccountObject).filter(AccountObject.uin == uin).first()

    @classmethod
    def handle_new_group(cls, query_item, **kwargs_update_info):
        kwargs_update_info['is_monitored'] = \
            kwargs_update_info.get('is_monitored',
                                   query_item.is_monitored if query_item else True)
        if query_item is None:
            new_group = add_group_kwargs(**kwargs_update_info)
            return new_group
        else:
            kwargs_update_info.pop('account_id')
            if is_monitoring(query_item.account_id, query_item.group_id):
                set_monitoring(query_item.account_id, kwargs_update_info['group_id'], True)
            query_item.update(**kwargs_update_info)
            # set_monitoring(query_item.account_id, query_item.group_id, kwargs_update_info['is_monitored'])
            return query_item

    @classmethod
    def find_old_group(cls, uin, nick_name, member_count):
        return db.session.query(GroupObject).filter(and_(GroupObject.uin == uin,
                                                         GroupObject.nick_name == nick_name)).first()

    @classmethod
    def handle_new_chatroom(cls, query_item, **kwargs_update_info):
        if query_item is None:
            new_chatroom = add_group_kwargs(**kwargs_update_info)
            return new_chatroom
        else:
            query_item.update(**kwargs_update_info)
            return query_item

    @classmethod
    def find_old_chatroom(cls, chatroom_id):
        return db.session.query(GroupObject).filter(GroupObject.chatroom_id == chatroom_id).first()

    @classmethod
    def handle_new_contact(cls, query_item, **kwargs_update_info):
        default_is_monitored = query_item.is_monitored if query_item else True
        is_monitored = kwargs_update_info.get('is_monitored', default_is_monitored)
        if query_item is None:
            new_contact = add_contact_new(kwargs_update_info['account_dict']['uin'],
                                          kwargs_update_info['account_dict']['uuid'],
                                          kwargs_update_info['contact_dict'],
                                          kwargs_update_info['contact_head'],
                                          is_monitored)
            # set_monitoring(new_contact.account_id, new_contact.contact_id, is_monitored)
            return new_contact
        else:
            # update monitor cache, stay if not specified
            # set_monitoring(query_item.account_id, kwargs_update_info['contact_dict']['UserName'],
            #                is_monitored)
            update_contact_new(query_item,
                               kwargs_update_info['contact_dict'],
                               is_monitored,
                               kwargs_update_info['contact_head'])
            return query_item

    @classmethod
    def find_old_contact(cls, uin, nick_name, alias=''):
        if alias != '':
            return db.session.query(ContactObject).filter(and_(ContactObject.uin == uin,
                                                               ContactObject.alias == alias)).first()
        return db.session.query(ContactObject).filter(and_(ContactObject.uin == uin,
                                                           ContactObject.nick_name == nick_name)).first()

    @classmethod
    def handle_new_member(cls, query_item, account_uin, group_id, group_uuid, member_dict, member_head):
        if query_item is None:
            new_member = add_member(account_uin, group_id, member_dict, group_uuid, member_head)
            return new_member
        else:
            update_member_new(query_item, account_uin, group_id, member_dict, group_uuid, member_head)
            return query_item

    @classmethod
    def find_old_member(cls, group_uuid, member_nick_name, account_uin):
        return db.session.query(MemberObject).filter(and_(MemberObject.group_uuid == group_uuid,
                                                          MemberObject.nick_name == member_nick_name,
                                                          MemberObject.uin == account_uin)
                                                     ).first()
