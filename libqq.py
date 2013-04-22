#coding: u8

import json
import logging
import random
import time
from itertools import count

import net


r = lambda: random.random()
t = lambda: time.time()
# 本方发送消息的id防止重复发送
tick = count(int(r() * 999999) + 12345678)

n = net.Net()


class Coco(object):
    UPDATE_STATUS = 0x01
    MESSAGE = 0x02
    FORCE_OFFLINE = 0x03

    def __init__(self, status='online'):
        self.status = status
        self.clientid = int((r() * 89999999)) + 10000000
        # 有时候可能会收到相同的消息，通过对方传来的msg_id可以判断
        # 如果已经在msg_ids中那么就丢弃此消息
        self.msg_ids = []
        # 心跳次数
        self.tip_id = int(r() * 999999)
        # 缓存所有信息
        from collections import defaultdict
        l = lambda: defaultdict(l)
        self.friend_cache = defaultdict(l)
        '''
        对每个uin缓存的数据有:
        {
        登录后会立即获取以下数据:
            'status': 好友在线状态
            'client_type': 客户端类型
            'nick': 备注或者昵称

        点击用户名字后才会获取以下数据:
            'face': 头像的二进制
            'lnick': 个性签名
            'qq': 好友真实的qq号码
        }
        '''

    def login(self, qq, pwd, vc=None):
        '''登录'''
        self.qq = qq
        self.pwd = pwd
        if vc is not None:
            # 如果给定了验证码则是用户已经输入了验证码才会进入此if语句
            self.vc = vc
            state = 0
        else:
            # 检查是否需要验证码
            url = 'https://ssl.ptlogin2.qq.com/check?uin={0}&appid=1003903&r={1}'
            url = url.format(self.qq, r())
            logging.debug('checking verifycode...')
            state, vc, uin = self.jsonp2list(n.get(url))
            self.uin = self._hex2chr(uin.replace('\\x', ''))
            self.vc = vc
        if state == '0':
            logging.debug('no need verifycode.')
            return {'need_verify_code': False, 'msg': self._login()}
        if state == '1':
            # 要验证码
            logging.debug('need verifycode!')
            return {'need_verify_code': True, 'data': self._get_verifycode()}

    def _login(self):
        logging.debug('logining...')
        self._encode_pwd()
        url = 'http://ptlogin2.qq.com/login?u={0}&p={1}&verifycode={2}&webqq_type=40&remember_uin=1&login2qq=1&aid=1003903&u1=http%3A%2F%2Fweb.qq.com%2Floginproxy.html%3Flogin2qq%3D1%26webqq_type%3D40&h=1&ptredirect=0&ptlang=2052&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=4-3-2475914&mibao_css=m_webqq&t=1&g=1'
        url = url.format(self.qq, self.encoded_pwd, self.vc.upper())
        jsn = self.jsonp2list(n.get(url))
        msg = unicode(jsn[4], 'u8')
        if u'登录成功' in msg:
            logging.debug('login success.')
            self._get_psession_id(self.status)
            self.nick = unicode(jsn[5], 'u8')
            logging.debug(u'nick: {0}.'.format(self.nick))
        else:
            logging.debug('login fail!')
            logging.debug(u'error msg: {0}.'.format(msg))
            return msg

    def poll(self):
        if not hasattr(self, 'psessionid'):
            return
        logging.debug('polling...')
        n.headers.update({
            'Referer': 'https://d.web2.qq.com/proxy.html?v=20110412001&callback=1&id=3'
        })
        url = 'http://d.web2.qq.com/channel/poll2'
        r = {
            'key': 0,
            'ids': [],
            'clientid': self.clientid,
            'psessionid': self.psessionid}
        r = json.dumps(r)
        jsn = n.post(url, {'r': r, 'clientid': self.clientid, 'psessionid': self.psessionid})
        res = json.loads(jsn)
        retcode = res['retcode']
        if retcode == 0:
            for i in res['result']:
                poll_type = i['poll_type']
                value = i['value']
                if poll_type == 'buddies_status_change':
                    yield {'msg': self.UPDATE_STATUS}
                elif poll_type == 'message':
                    msg_id = value['msg_id']
                    if msg_id not in self.msg_ids:
                        self.msg_ids.append(msg_id)
                        yield {'msg': self.MESSAGE, 'data': value}
                    else:
                        i['poll_type'] = 'same message'
        elif retcode == 121:
            yield {'msg': self.FORCE_OFFLINE}

    def get_face(self, uin=None):
        '''获取头像'''
        if uin is None:
            uin = self.qq
        else:
            face = self.friend_cache[uin].get('face')
            if face is not None:
                return face
        logging.debug('getting face image of %s...' % uin)
        url = 'http://face%s.qun.qq.com/cgi/svr/face/getface?cache=1&type=1&fid=0&uin=%s&vfwebqq=%s'
        url %= random.randint(1, 9), uin, self.vfwebqq
        face = n.get(url)
        logging.debug('%s\'s face image gotten.' % uin)
        if uin == self.qq:
            self.face = face
        else:
            self.friend_cache[uin]['face'] = face
        return face

    def _encode_pwd(self):
        from hashlib import md5 as _md5
        md5 = lambda x: _md5(x).hexdigest().upper()
        self.encoded_pwd = md5(
            md5(self._hex2chr(md5(self.pwd)) + self.uin) + self.vc.upper())

    def _get_psession_id(self, status):
        logging.debug('getting psessionid...')
        # 获取两个cookie的值
        self.skey = n.get_cookie('skey')
        self.ptwebqq = n.get_cookie('ptwebqq')
        r = {
            'status': status,
            'ptwebqq': self.ptwebqq,
            'passwd_sig': '',
            'clientid': self.clientid,
            'psessionid': 'null'}
        r = json.dumps(r)
        url = 'https://d.web2.qq.com/channel/login2'
        # Referer很重要，不然会返回103
        n.headers.update({
            'Referer': 'https://d.web2.qq.com/proxy.html?v=20110412001&callback=1&id=3'
        })
        jsn = n.post(url, {'r': r, 'clientid': self.clientid, 'psessionid': 'null'})
        result = json.loads(jsn)['result']
        self.vfwebqq = result['vfwebqq']
        self.psessionid = result['psessionid']
        self.status = result['status']
        logging.debug('psessionid gotten.')

    def get_my_level(self):
        logging.debug('getting my level...')
        '''获取等级'''
        url = 'http://s.web2.qq.com/api/get_qq_level2?tuin=%s&vfwebqq=%s&t=%s'
        url %= self.qq, self.vfwebqq, t()
        self.level = json.loads(n.get(url))['result']
        logging.debug('my level gotten.')
        return self.level

    def get_long_nick(self, uin=None):
        '''个性签名'''
        if uin is None:
            uin = self.qq
        else:
            lnick = self.friend_cache[uin].get('lnick')
            if lnick is not None:
                return lnick
        logging.debug('getting long nick of %s ...' % uin)
        url = 'http://s.web2.qq.com/api/get_single_long_nick2?tuin=%s&vfwebqq=%s&t=%s'
        url %= uin, self.vfwebqq, t()
        lnick = json.loads(n.get(url))['result'][0]['lnick']
        logging.debug(u'%s\'s long nick is %s.' % (uin, lnick))
        if uin == self.qq:
            self.lnick = lnick
        else:
            self.friend_cache[uin]['lnick'] = lnick
        return lnick

    def get_my_friends_info(self):
        '''得到好友列表及分组信息(即主面板中的数据)'''
        logging.debug('getting my friends info...')
        url = 'http://s.web2.qq.com/api/get_user_friends2'
        n.headers.update({
            'Referer': 'https://d.web2.qq.com/proxy.html?v=20110412001&callback=1&id=3'
        })
        r = {'h': 'hello', 'vfwebqq': self.vfwebqq, 'hash': self._hash2()}
        jsn = n.post(url, {'r': json.dumps(r)})
        #file('friends_list', 'w').write(jsn)
        self.friends_info = json.loads(jsn)['result']
        logging.debug('my friends info gotten.')
        self._handle_friends_info()
        return self.friends_info

    def _handle_friends_info(self):
        '''根据好友列表数据格式化好'''
        i = self.friends_info

        # 所有好友
        key = lambda x: x['categories']
        friends = sorted(i['friends'], key=key)
        from itertools import groupby, imap
        self.friends = {k: list(g) for k, g in groupby(friends, key=key)}
        # {k: g} k为群组的index, g为组下的所有好友列表

        # 分组
        self.categories = sorted(i['categories'], key=lambda x: x['sort'])
        # 有备注的好友[uin为key]
        marknames = dict(imap(
            lambda x: (x['uin'], x['markname']), i['marknames']))
        # 所有好友的信息[uin为key]
        info = dict(imap(lambda x: (x['uin'], x['nick']), i['info']))
        # 将有备注的替换掉昵称
        info.update(marknames)
        # 存放到缓存
        for uin, nick in info.iteritems():
            self.friend_cache[uin]['nick'] = nick
            # 默认为离线状态
            self.friend_cache[uin].setdefault('status', 'offline')
        # vipinfo应该是会员信息，没用,舍弃

    def _hash2(self):
        '''新的hash算法http://0.web.qstatic.com/webqqpic/pubapps/0/50/eqq.all.js?t=20130417001第596行'''
        b = self.qq
        i = self.ptwebqq
        a = i + 'password error'
        s = ''
        j = []
        while 1:
            if len(s) <= len(a):
                s += b
                if len(s) == len(a):
                    break
            else:
                s = s[:len(a)]
                break
        for d in range(len(s)):
            j.append(ord(s[d]) ^ ord(a[d]))

        import string
        a = list(string.digits) + ['A', 'B', 'C', 'D', 'E', 'F']
        s = ''
        for d in j:
            s += a[d >> 4 & 15]
            s += a[d & 15]
        return s

    def _hash(self):
        '''某时的hash，已经失效http://0.web.qstatic.com/webqqpic/pubapps/0/50/eqq.all.js搜索GetBuddyList'''
        a = self.qq
        e = self.ptwebqq
        l = len(e)
        # 将qq号码转换成整形列表
        b, k, d = 0, -1, 0
        for d in a:
            d = int(d)
            b += d
            b %= l
            f = 0
            if b + 4 > l:
                g = 4 + b - l
                for h in range(4):
                    f |= h < g and (
                        ord(e[b + h]) & 255) << (3 - h) * 8 or (
                            ord(e[h - g]) & 255) << (3 - h) * 8
            else:
                for h in range(4):
                    f |= (ord(e[b + h]) & 255) << (3 - h) * 8
            k ^= f
        c = [k >> 24 & 255, k >> 16 & 255, k >> 8 & 255, k & 255]
        import string
        k = list(string.digits) + ['A', 'B', 'C', 'D', 'E', 'F']
        d = [k[b >> 4 & 15] + k[b & 15] for b in c]
        return ''.join(d)

    def get_my_group_info(self):
        '''得到群组信息'''
        url = 'http://s.web2.qq.com/api/get_group_name_list_mask2'
        n.headers.update({
            'Referer': 'https://d.web2.qq.com/proxy.html?v=20110412001&callback=1&id=3'
        })
        jsn = n.post(url, {'r': json.dumps({'vfwebqq': self.vfwebqq})})
        self.groups_info = json.loads(jsn)['result']

    def get_online_list(self):
        '''在线列表'''
        logging.debug('getting online list...')
        url = 'http://d.web2.qq.com/channel/get_online_buddies2?clientid=%s&psessionid=%s'
        url %= self.clientid, self.psessionid

        online_list = json.loads(n.get(url))['result']
        #file('online_list', 'w').write(json.dumps(online_list))
        for one in online_list:
            uin = one['uin']
            # 状态
            self.friend_cache[uin]['status'] = one['status']
            # 客户端类型
            self.friend_cache[uin]['client_type'] = one['client_type']
        logging.debug('online list gotten.')

    def send_msg_to_friend(self, uin, msg, font=None):
        '''发送消息'''
        if isinstance(msg, unicode):
            msg = msg.encode('u8')
        font = font or {
            'name': '宋体',
            'size': '12',
            'style': [0, 0, 0],
            'color': '000000'
        }
        name = font['name']
        if isinstance(name, unicode):
            font['name'] = name.encode('u8')
        url = 'http://d.web2.qq.com/channel/send_buddy_msg2'
        n.headers.update({
            'Referer': 'https://d.web2.qq.com/proxy.html?v=20110412001&callback=1&id=3'
        })
        style = ','.join(map(str, font['style']))
        msg = '[' + msg + '["font",{"name":"' + name + '","size":"' + \
              font['size'] + '","style":[' + style + '],"color":"' + \
              font['color'] + '"}]]'
        r = {
            'to': str(uin),
            'face': 0,
            'msg_id': tick.next(),
            'content': msg,
            'clientid': self.clientid,
            'psessionid': self.psessionid
        }
        jsn = n.post(url, {
            'r': json.dumps(r),
            'clientid': self.clientid,
            'psessionid': self.psessionid
        })
        return json.loads(jsn)

    def get_bulk_lnick(self):
        '''批量得到好友的个性签名'''
        l = map(str, self.online_list.keys())
        url = 'http://s.web2.qq.com/api/get_long_nick?tuin=%s&vfwebqq=%s&t=%s'
        url %= '[' + ','.join(l) + ']', self.vfwebqq, t()
        self.personal = json.loads(n.get(url))['result']

    def get_recent_list(self):
        url = 'http://d.web2.qq.com/channel/get_recent_list2'
        n.headers.update({
            'Referer': 'https://d.web2.qq.com/proxy.html?v=20110412001&callback=1&id=3'
        })
        r = {
            'vfwebqq': self.vfwebqq,
            'clientid': self.clientid,
            'psessionid': self.psessionid}
        jsn = n.post(url, {
            'r': json.dumps(r),
            'clientid': self.clientid,
            'psessionid': self.psessionid
        })
        self.recent_list = json.loads(jsn)['result']

    def get_profile(self, uin=None):
        # 我的个人资料
        uin = uin or self.qq
        logging.debug('getting my profile...')
        url = 'http://s.web2.qq.com/api/get_friend_info2?tuin=%s&verifysession=&code=&vfwebqq=%s&t=%s'
        url %= uin, self.vfwebqq, t()
        profile = json.loads(n.get(url))['result']
        logging.debug('my profile gotten.')
        if uin == self.qq:
            self.profile = profile
        return profile

    def uin2qq(self, uin):
        '''根据给定的uin，得到好友的qq'''
        qq = self.friend_cache[uin].get('qq')
        if qq is not None:
            return qq
        logging.debug('getting qq of uin: %s' % uin)
        url = 'http://s.web2.qq.com/api/get_friend_uin2?tuin=%s&verifysession=&type=1&code=&vfwebqq=%s'
        url %= uin, self.vfwebqq
        n.headers.update({
            'Referer': 'https://d.web2.qq.com/proxy.html?v=20110412001&callback=1&id=3'
        })
        try:
            qq = json.loads(n.get(url))['result']['account']
        except KeyError:
            return
        self.friend_cache[uin]['qq'] = qq
        logging.debug('%s\'s qq is %s' % (uin, qq))
        return qq

    def get_msg_tip(self):
        '''心跳，不过好像用poll了，这个没什么用？'''
        import time
        while 1:
            time.sleep(60)
            try:
                url = 'http://web.qq.com/web2/get_msg_tip?uin=&tp=1&id=0&retype=1&rc=%s&lv=3&t=%s'
                url %= self.tip_id, t()
                yield json.loads(n.get(url))
                self.tip_id += 1
            except:
                pass

    def get_offpic(self, file_path, f_uin):
        '''得到离线图片'''
        url = 'http://d.web2.qq.com/channel/get_offpic2?file_path=%s&f_uin=%s&clientid=%s&psessionid=%s'
        url %= file_path, f_uin, self.clientid, self.psessionid
        return n.get(url)

    def _get_verifycode(self):
        '''获取验证码'''
        url = 'http://captcha.qq.com/getimage?aid=1003903&r=%s&uin=%s&vc_type=%s'
        url %= r(), self.qq, self.vc
        logging.debug('getting verifycode')
        return n.get(url)

    def _hex2chr(self, s):
        return ''.join([chr(int(''.join(h), 16)) for h in self.group(s, 2)])

    def _updateOnlineList(self, v):
        print '# TODO '
        return
        fd = 0
        for i in v:
            if i['uin'] == v.uin:
                fd = 1
                if v['status'] == 'offline':
                    return fd

    @staticmethod
    def group(seq, size):
        def take(seq, n):
            for i in xrange(n):
                yield seq.next()

        if not hasattr(seq, 'next'):
            seq = iter(seq)
        while True:
            x = list(take(seq, size))
            if x:
                yield x
            else:
                break

    @staticmethod
    def jsonp2list(jsonp):
        args = jsonp[jsonp.find('(') + 1: jsonp.rfind(')')]
        return [i.strip("' ") for i in args.split(',')]


def test():
    coco = Coco()
    fail = coco.login('123456', '123456')
    if not fail['need_verify_code']:
        if fail['msg'] is not None:
            print fail
            return
    else:
        print 'need_verify_code'
        return
    # 头像
    #print coco.get_face()
    #print coco.face

    # 个人资料
    #print coco.get_profile()
    #print coco.profile

    # 等级
    #print coco.get_my_level()
    #print coco.level

    # 个性签名
    #print coco.get_long_nick()
    #print coco.lnick

    # 得到好友信息(主面板)
    #print coco.get_my_friends_info()
    #print coco.friends_info

    # 得到群组信息(主面板)
    #coco.get_my_group_info()
    #print coco.groups_info

    # 在线列表
    #coco.get_online_list()
    #print coco.online_list

    # 好友信息
    # coco.get_bulk_lnick()
    # print coco.personal

    # 最近消息
    #coco.get_recent_list()
    #print coco.recent_list


if __name__ == '__main__':
    test()
    import doctest
    doctest.testmod()
