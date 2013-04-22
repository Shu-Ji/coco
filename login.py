#coding: u8

from PyQt4.QtGui import QApplication, QMessageBox
from PyQt4.QtCore import QThread, QPoint, SIGNAL


class LoginVcThread(QThread):
    def __init__(self, login_handler):
        signal = SIGNAL('login vc finish')
        self.mw = login_handler.mw
        self.mw.connect(self.mw, signal, login_handler.login_vc_finish)
        self.signal = signal

        QThread.__init__(self)

    def run(self):
        msg = self.mw.coco._login()
        self.mw.emit(self.signal, msg)


class LoginThread(QThread):
    def __init__(self, login_handler):
        from PyQt4.QtCore import SIGNAL
        signal = SIGNAL('login finish')
        self.mw = login_handler.mw
        self.mw.connect(self.mw, signal, login_handler.login_finish)
        self.signal = signal

        QThread.__init__(self)

    def set_data(self, qq, pwd):
        self.qq, self.pwd = qq, pwd

    def run(self):
        res = self.mw.coco.login(self.qq, self.pwd)
        self.mw.emit(self.signal, res)


class LoginHandler:
    def __init__(self, mainwindow):
        self.mw = mainwindow
        self.login_thread = None
        self.login_vc_thread = None

        self.init_ui()
        self.init_event()
        self.init_connect()

    def init_ui(self):
        # 设置窗口大小(300, 700)
        this = self.mw
        w = 300
        h = 700
        this.setMinimumSize(w, h)
        this.setMaximumSize(w, h)

        # 将窗口移动到屏幕右边
        d = QApplication.desktop()
        this.move((d.width() - w) / 2, (d.height() - h) / 2)

    def init_connect(self):
        this = self.mw
        this.login_btn.clicked.connect(self.on_click_login_btn)
        this.login_loading_btn.clicked.connect(self.on_click_login_loading_btn)
        this.login_loading_login_btn.clicked.connect(
            self.on_click_login_loading_login_btn)

    def on_click_login_loading_login_btn(self):
        '''用户输入验证码后点击登录'''
        this = self.mw
        coco = this.coco
        vc = str(this.login_input_vc.text())
        if not vc:
            this.login_input_vc.setFocus()
            return QMessageBox.critical(this, u'提示', u'请输入验证码')

        this.login_loading_label.show()
        this.login_vcimg.hide()
        this.login_input_vc.hide()

        coco.vc = vc
        # 登录
        if self.login_vc_thread is None:
            self.login_vc_thread = LoginVcThread(self)
        self.login_vc_thread.start()

    def login_vc_finish(self, msg):
        if msg is None:
            # 登录成功
            return self.init_body()

        this = self.mw
        QMessageBox.critical(this, u'错误', msg)

        this.login_loading_label.hide()
        this.login_vcimg.show()
        this.login_input_vc.show()

        if u'密码' in msg:
            this.login_loading_btn.click()
            this.login_input_pwd.setFocus()
            this.login_input_pwd.selectAll()
        else:
            self.set_verify_code(this.coco._get_verifycode())
            this.login_input_vc.setFocus()
            this.login_input_vc.selectAll()

    def init_event(self):
        this = self.mw
        this.login_panel.mouseMoveEvent = self.mouseMoveEvent
        this.login_panel.mousePressEvent = self.mousePressEvent
        this.login_panel.mouseReleaseEvent = self.mouseReleaseEvent

    def mouseMoveEvent(self, e):
        try:
            newpos = QPoint(e.globalPos())
            upleft = QPoint(self._pos0 + newpos - self._last)
            self.mw.move(upleft)
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

    def on_click_login_loading_btn(self):
        this = self.mw
        this.login_loading_area.hide()
        this.loginarea.show()
        try:
            self.login_thread.terminate()
            self.login_vc_thread.terminate()
        except AttributeError:
            pass
        this.login_btn.setEnabled(True)

    def on_click_login_btn(self):
        this = self.mw
        this.login_btn.setEnabled(False)
        # 隐藏验证码图片
        this.login_vcimg.hide()
        this.login_input_vc.hide()
        this.login_input_vc.setText('')
        this.login_loading_label.show()

        qq = str(this.login_input_qq.text())
        pwd = str(this.login_input_pwd.text())

        import re
        if not re.match(r'^\d{4,10}$', qq):
            QMessageBox.critical(this, u'格式错误', u'QQ号码只能是数字')
            this.login_btn.setEnabled(True)
            this.login_input_qq.setFocus()
            return this.login_input_qq.selectAll()

        this.loginarea.hide()
        this.login_loading_area.show()
        # 登录
        if self.login_thread is None:
            self.login_thread = LoginThread(self)
        self.login_thread.set_data(qq, pwd)
        self.login_thread.start()

    def login_finish(self, res):
        this = self.mw
        this.login_btn.setEnabled(True)
        if not res['need_verify_code']:
            msg = res['msg']
            if msg is not None:
                QMessageBox.critical(this, u'登录失败', msg)
                this.login_loading_btn.click()
                this.login_input_pwd.setFocus()
                return this.login_input_pwd.selectAll()
            # 登录成功
            return self.init_body()

        # 需要验证码
        this.login_loading_label.hide()
        self.set_verify_code(res['data'])
        this.login_input_vc.show()
        this.login_input_vc.setFocus()

    def set_verify_code(self, data):
        this = self.mw
        from PyQt4.QtGui import QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        this.login_vcimg.setPixmap(pixmap)
        this.login_vcimg.show()

    def init_body(self):
        this = self.mw
        this.login_panel.hide()

        '''
        # 获取屏幕大小
        d = QApplication.desktop()
        w = d.width()
        h = d.height()
        # 设置程序大小为屏幕的五分之四大小
        ww = 4 * w / 5
        wh = 4 * h / 5
        this.resize(ww, wh)
        this.setMinimumSize(ww, wh)
        this.move((w - this.width()) / 2, (h - this.height()) / 2)
        s = 9999
        this.main_widget.setMaximumSize(s, s)
        this.setMaximumSize(s, s)
        '''

        # 通知主窗口登录成功，可以获取好友列表等信息了
        this.emit(SIGNAL('login success'))
