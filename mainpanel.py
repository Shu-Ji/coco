#coding: u8

import json
import thread
import logging

from PyQt4.QtCore import QPoint, SIGNAL, QSize

import models
import template
import settings

db = models.db
render = template.Render(
    debug=settings.DEBUG,
    trim_blocks=True,
    line_comment_prefix='^^',
    line_statement_prefix='^',
)


def require(path):
    '''由于qrc文件转换成了py文件，所以后面加载的文件(js/css)都是以前的'''
    if settings.DEBUG:
        # 从本地文件加载而不是从qrc中
        import os
        import os.path as osp
        ext = osp.splitext(path)[1][1:]
        if ext == 'ogg':
            p = osp.join(os.getcwd(), 'res/snd/%s' % path)
            p = 'file://%s' % p
        elif ext in ['js', 'css']:
            path = osp.join(os.getcwd(), 'res/static/%s/%s' % (ext, path))

            # 禁止读取缓存
            import time
            path += '?t=%s' % str(time.time())

            if ext == 'css':
                p = u'<link rel="stylesheet" href="file://%s"></style>' % path
            elif ext == 'js':
                p = u'<script src="file://%s"></script>' % path
        elif ext in ['gif', 'png']:
            p = 'file://%s' % osp.join(os.getcwd(), 'res/img/%s' % path)
        return p
    else:
        if ext == 'css':
            path = 'qrc:///%s' % path
            return '<link rel="stylesheet" href="%s">' % path
        elif ext == 'js':
            path = 'qrc:///%s' % path
            return '<script src="%s"></script>' % path
        elif ext == 'ogg':
            return 'qrc:///%s' % path
        elif ext in ['gif', 'png']:
            return 'qrc:///img/%s' % path


def get_offpic_data(pk):
    '''根据给定的pk得到图片的二进制数据'''
    I = models.ImageStorage
    pic = db.query(I.data).filter_by(pk=pk).first()
    return None if pic is None else get_img_base64(pic.data)


def get_img_base64(img_binary):
    '''返回用于img标签的src的base64字串'''
    import base64
    import magic
    ms = magic.open(magic.MAGIC_MIME)
    ms.load()
    try:
        mime_type = ms.buffer(img_binary).split(' ', 1)[0]
    except Exception:
        mime_type = 'image/png;'
    return 'data:%sbase64,%s' % (mime_type, base64.b64encode(img_binary))


render._lookup.globals.update({
    'json': json,
    'require': require,
    'offpic_data': get_offpic_data,
})


def runonce(func, *args, **kwargs):
    def _funcwrapper():
        import time
        logged = False
        while 1:
            try:
                time.sleep(0.1)
                return func(*args, **kwargs)
            except AttributeError:
                continue
            except Exception, e:
                if not logged:
                    logging.debug(
                        '{0} in function: {1}'.format(e, func.__name__))
                    logging.debug('trying again...')
                logged = True
    if not (args and kwargs):
        return thread.start_new_thread(_funcwrapper, ())
    return thread.start_new_thread(_funcwrapper, *args, **kwargs)


class MainHandler:
    def __init__(self, mainwindow):
        self.mw = mainwindow
        self.login_thread = None
        self.last_windowsize = None
        # 我的头像的base64数据
        self.avatar_base64 = None

        this = self.mw
        self.web_view = this.web_view

        self.init_event()
        self.init_connect()

        # 可手动区域
        self.MOVE_HANDLE_HEIGHT = 100

    def init_ui(self):
        this = self.mw
        this.main_widget.show()
        # 隐藏聊天窗口
        this.content_panel.hide()
        # 昵称
        this.nick.setText(self.coco.nick)
        # 头像
        runonce(self.get_my_face)
        # 在线列表
        runonce(self.get_online_list)
        # 主面板好友列表
        runonce(self.get_my_friends_info)

        #runonce(self.coco.get_profile)
        #runonce(self.coco.get_my_level)
        #runonce(self.coco.get_my_long_nick)

        # 输入框
        this.input_div.setHtml(render('editor.html'))
        # 后台功能，如播放声音等等
        this.background_view.setHtml(render('background.html'))

    def get_my_friends_info(self):
        this = self.mw
        self.coco.get_my_friends_info()
        this.emit(SIGNAL('get friends info success'))

    def get_online_list(self):
        this = self.mw
        self.coco.get_online_list()
        this.emit(SIGNAL('get online list success'))

    @property
    def coco(self):
        return self.mw.coco

    def get_my_face(self):
        this = self.mw
        avatar = self.coco.get_face()
        this.emit(SIGNAL('get face success'), avatar)

    def set_face_img(self, avatar):
        from PyQt4.QtGui import QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(avatar)
        self.avatar_base64 = avatar
        self.mw.avatar.setPixmap(pixmap)

    def init_connect(self):
        this = self.mw
        this.connect(this, SIGNAL('get face success'), self.set_face_img)
        this.connect(
            this, SIGNAL('get friends info success'), self.init_main_panel)
        this.friends_list_tree.itemClicked.connect(self.on_click_tree_item)

        this.session_list_widget.itemClicked.connect(
            self.on_click_session_list_widget_item)
        # 新消息来临的时候通知窗口更新
        this.connect(
            this, SIGNAL('click_list_item(PyQt_PyObject, PyQt_PyObject)'),
            self.show_main_panel)

        this.toggle_btn.clicked.connect(self.toggle_window_size)
        this.connect(
            this, SIGNAL('get online list success'), self.update_status)
        this.connect(this, SIGNAL('resort list'), self.resort_list)
        this.connect(this, SIGNAL('get flnick success'), self.set_flnick)
        this.connect(this, SIGNAL('get face image success'), self.set_fface)
        this.send_btn.clicked.connect(self.send_friend_msg)
        this.connect(
            this, SIGNAL('can load history'), self.load_friend_history)
        this.connect(
            this, SIGNAL('set session list item'),
            lambda item: self.mw.session_list_widget.setCurrentRow(0)
        )
        this.connect(this, SIGNAL('play sound'), self.play_sound)

    def play_sound(self, snd_str):
        self.call_js_function('playSound("%s")' % snd_str, self.mw.background_view)

    def send_friend_msg(self, uin=None, msg=None, font=None):
        '''点击发送消息给好友'''
        this = self.mw
        uin = uin or self.get_element(
            '#content', this.web_view).attribute('data-uin')
        # 调用javascript对发送的数据进行解析
        msg = msg or self.call_js_function(
            'formatMsg()', this.input_div).toPyObject()

        def _send_msg():
            # FIXME: 字体
            font = {
                'name': '宋体',
                'size': '16',
                'style': [0, 0, 0],
                'color': '000000'
            }
            content = self.qstring2pystr(msg).strip()
            if not content:
                return
            # 将消息保存到数据库
            content_str = '[' + content.rstrip(',') + ']'
            _content = json.loads(content_str)
            data = {'font': font, 'msg': self.analyze_msg(_content)}
            _uin = self.coco.uin2qq(uin)
            self.save_history(self.coco.qq, _uin, json.dumps(data))

            # 更新显示区域
            def _load_history():
                from_qq = self.coco.uin2qq(uin)
                this.emit(SIGNAL('can load history'), from_qq, uin)
            runonce(_load_history)

            ret = self.coco.send_msg_to_friend(uin, content, font)
            # 重复发送直到发送成功
            if ret['retcode'] != 0 and ret['result'] != 'ok':
                logging.debug('send message fail, returned msg:')
                logging.debgug(ret)
                self.send_friend_msg(uin, msg, font)

        runonce(_send_msg)
        this.input_div.setFocus()

    def call_js_function(self, func_str, view):
        '''调用javascript中的函数'''
        return self.get_main_frame(view).evaluateJavaScript(func_str)

    def get_element(self, selector, view):
        '''返回元素'''
        return self.get_main_frame(view).findFirstElement(selector)

    def get_main_frame(self, view):
        '''得到页面的mainFrame'''
        return view.page().mainFrame()

    def on_click_session_list_widget_item(self, item):
        self.show_main_panel(item.uin)

    def analyze_msg(self, content, uin=None):
        '''解析msg，方便以后保存到数据库'''
        msg = []
        for i in content:
            if isinstance(i, unicode):
                i = i.replace(
                    u'【提示：此用户正在使用Q+ Web：http://web.qq.com/】', '')
                msg.append({'unicode': i})
            elif isinstance(i, list):
                type_ = i[0]
                if type_ == 'face':
                    msg.append({'face': i[1]})
                elif type_ == 'offpic':
                    file_path = i[1]['file_path']
                    img = self.coco.get_offpic(file_path, uin)
                    # 将图片存入到数据库
                    img = models.ImageStorage(data=img)
                    db.add(img)
                    db.commit()
                    msg.append({'offpic': img.pk})
        return msg

    def new_friend_msg(self, msg):
        '''有新对话'''
        this = self.mw
        uin = msg['from_uin']
        content = msg['content']
        font = content[0][1]
        content = content[1:]
        msg = self.analyze_msg(content, uin)
        if not msg:
            return

        nick = self.coco.friend_cache[uin]['nick']
        # 添加到会话列表中
        exists = False
        lw = this.session_list_widget
        for i in range(lw.count()):
            item = lw.item(i)
            if item.uin == uin:
                exists = True
                break
        if not exists:
            from PyQt4.QtGui import QListWidgetItem as Lwi
            item = Lwi(nick, lw)
            item.uin = uin

        # 如果当前正在和这个好友聊天，那么更新聊天窗口的历史记录
        # FIXME: 这会使得页面滚动到底部，如果用户正在查看上面的历史信息，会强制
        # 他到底部来，需要在click事件中做处理
        ci = lw.currentItem()
        _signal = SIGNAL('click_list_item(PyQt_PyObject, PyQt_PyObject)')
        if ci is None:
            # 如果用户一个会话都还没有
            this.emit(SIGNAL('set current session list item'), item)
            this.emit(_signal, uin, False)
        elif ci.uin == uin:
            # 如果是当前正在聊天的好友的消息，那么更新聊天历史显示区域
            this.emit(_signal, uin, True)

        # 显示会话tab
        this.tab_widget.setCurrentIndex(2)

        data = {'font': font}
        data['msg'] = msg
        content = json.dumps(data)
        from_qq = self.coco.uin2qq(uin)
        self.save_history(from_qq, self.coco.qq, content, nick)

        # 不能直接调用js的函数，因为poll是在多线程中
        this.emit(SIGNAL('play sound'), 'msg')
        self.show_main_panel(uin)

    def save_history(self, from_, to, content, friend_name=None):
        db.add(models.FriendHistory(
            from_uin=from_, to_uin=to, friend_name=friend_name,
            content=content))
        db.commit()

    def update_status(self):
        '''更新好友列表'''
        # 因为是多线程，所以可能好友列表还没有获取到所以用runonce来包一下
        # 即要等到self.root存在的时候才正常进行下去，self.root在init_main_panel
        # 中得到初始化的，表示树
        def _run_update_status():
            getattr(self, 'root')
            self.mw.emit(SIGNAL('resort list'))
        runonce(_run_update_status)

    def resort_list(self):
        hidden = ['hidden', 'offline']
        from PyQt4.QtGui import QBrush, QColor
        for group_item in self.root:
            need_del = set()
            total_cnt = group_item.childCount()
            for i in range(total_cnt):
                c = group_item.child(i)
                uin = c.uin
                # 更新所有好友的状态
                status = self.coco.friend_cache[uin]['status']
                if status in hidden:
                    need_del.add(c)
            # 删除隐身或者不在线的
            for c in need_del:
                group_item.removeChild(c)
            # 添加到末尾
            for c in need_del:
                c.setForeground(0, QBrush(QColor(192, 192, 192, 100)))
                group_item.addChild(c)
            online_cnt = total_cnt - len(need_del)
            group_item.setText(0, u'{0}({1}/{2})'.format(
                group_item.text(0), online_cnt, total_cnt))
        logging.debug('online list resorted.')

    @staticmethod
    def qstring2pystr(qstring, en='u8'):
        '''将QString转换成python的str'''
        return MainHandler.qstring2pyunicode(qstring, en).encode(en)

    @staticmethod
    def qstring2pyunicode(qstring, en='u8'):
        '''将QString转换成python的unicode'''
        return unicode(qstring.toUtf8(), en, 'ignore')

    def set_flnick(self, flnick):
        '''设置对话框中的个性签名'''
        flnick = u'({0})'.format(flnick)
        self.mw.flnick_label.setText(flnick)

    def set_fface(self, avatar):
        '''设置对话框中的好友和我的头像'''
        view = self.mw.web_view
        gotop = self.get_element('#gotop', view)
        gotop.setAttribute('src', get_img_base64(avatar))
        gotop.setStyleProperty('display', 'block')

        # 设置自己的头像
        gotop_i = self.get_element('#gotop_i', view)
        gotop_i.setAttribute('src', get_img_base64(self.avatar_base64))
        gotop_i.setStyleProperty('display', 'block')

    def show_main_panel(self, uin, new_msg=False):
        '''显示聊天窗口,new_msg表示如果是新消息，那么只用更新历史区域，
        顶部的好友昵称和个性签名都不用更新'''
        this = self.mw
        this.toggle_btn.setChecked(True)
        self.set_window_size_big()

        # 获取好友的真实qq
        def _getqq():
            from_qq = self.coco.uin2qq(uin)
            this.emit(SIGNAL('can load history'), from_qq, uin)
        runonce(_getqq)

        if not new_msg:
            # 获取个性签名
            def _getlnick():
                flnick = self.coco.get_long_nick(uin)
                this.emit(SIGNAL('get flnick success'), flnick)
            # 显示好友名字
            this.friend_name_label.setText(self.coco.friend_cache[uin]['nick'])
            this.flnick_label.setText(u'正在获取个性签名...')
            runonce(_getlnick)

        # 点击编辑器
        self.mw.input_div.setFocus()

    def load_friend_history(self, from_qq, uin):
        '''得到某个好友的历史记录'''
        this = self.mw
        if from_qq is not None:
            H = models.FriendHistory
            qqs = [self.coco.qq, from_qq]
            history = db.query(H.content, H.dt, H.friend_name).filter(
                H.to_uin.in_(qqs), H.from_uin.in_(qqs)).order_by(
                    H.dt.desc()).limit(50)
        else:
            history = []

        # 是否是我的消息，如果不是，那么播放声音
        this.web_view.setHtml(render('body.html', uin=uin, history=history))
        this.input_div.setHtml(render('editor.html'))

        # 将this暴露给js
        self.get_main_frame(this.input_div).addToJavaScriptWindowObject(
            'mainwindow', this)

        # 只有在加载完成历史记录即渲染好了页面之后才能加载头像
        # 获取头像
        def _getfface():
            avatar = self.coco.get_face(uin)
            this.emit(SIGNAL('get face image success'), avatar)
        runonce(_getfface)

    def on_click_tree_item(self, item):
        if item.childCount() > 0:
            item.setExpanded(not item.isExpanded())
        else:
            self.show_main_panel(item.uin)

    def set_window_size_big(self):
        this = self.mw
        this.content_panel.show()
        # 获取屏幕大小
        from PyQt4.QtGui import QApplication
        d = QApplication.desktop()
        w = d.width()
        h = d.height()
        # 设置程序大小为屏幕的五分之四大小
        ww = 4 * w / 5
        wh = 4 * h / 5
        this.resize(ww, wh)
        this.setMinimumSize(ww, wh)
        self._min_height = wh
        s = 9999
        this.main_widget.setMaximumSize(s, s)
        this.setMaximumSize(s, s)

    def set_window_size_small(self, w=300):
        # 设置窗口大小(300, 700)
        this = self.mw
        this.content_panel.hide()
        this.setMinimumSize(w, self._min_height)
        this.setMaximumSize(w, self._min_height)

    def toggle_window_size(self):
        if self.mw.content_panel.isHidden():
            self.set_window_size_big()
        else:
            self.set_window_size_small()

    def init_main_panel(self):
        from PyQt4.QtGui import QTreeWidgetItem as Twi

        this = self.mw
        coco = self.coco
        tree = this.friends_list_tree
        self.root = []

        friends = coco.friends
        from copy import deepcopy
        # 有些好友并不在任何返回的群组中(可能是陌生人或者黑名单吧，没有测试过)
        friends_copy = deepcopy(friends)

        for cat in coco.categories:
            group_item = Twi(tree, [cat['name']])
            group_item.setSizeHint(0, QSize(0, 30))
            self.root.append(group_item)
            index = cat['index']
            friends_of_this_group = friends_copy.pop(index)
            for friend in friends_of_this_group:
                uin = friend['uin']
                # 有备注就取备注否则取昵称
                nick = coco.friend_cache[uin]['nick']
                t = Twi(group_item, [nick])
                # 将uin存储在item上
                t.uin = uin
                coco.friend_cache[uin]['nick'] = nick

        if friends_copy:
            logging.debug('thers are friends that not belong to any category.')

        tree.insertTopLevelItems(0, self.root)

    def init_event(self):
        this = self.mw
        this.main_panel.mouseMoveEvent = self.mouseMoveEvent
        this.main_panel.mousePressEvent = self.mousePressEvent
        this.main_panel.mouseReleaseEvent = self.mouseReleaseEvent

        this.main_widget.mouseMoveEvent = self.mouseMoveEvent
        this.main_widget.mousePressEvent = self.mousePressEvent
        this.main_widget.mouseReleaseEvent = self.mouseReleaseEvent

    def mouseMoveEvent(self, e):
        this = self.mw
        try:
            if ((self._last2.x() == -1) or (
                self._last2.x() >= 0 and self._last2.x() <= this.width() and (
                    self._last2.y() >= self.MOVE_HANDLE_HEIGHT) and (
                        self._last2.y() <= this.height()))):
                return
            newpos = QPoint(e.globalPos())
            upleft = QPoint(self._pos0 + newpos - self._last)
            this.move(upleft)
        except AttributeError:
            pass

    def mousePressEvent(self, e):
        try:
            self._last = e.globalPos()
            self._pos0 = e.globalPos() - e.pos()
            self._last2 = e.pos()
        except AttributeError:
            pass

    def mouseReleaseEvent(self, e):
        try:
            self._last2.setX(-1)
        except AttributeError:
            pass
