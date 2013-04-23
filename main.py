#! /usr/bin/env python
#coding: u8

import sys

from PyQt4.QtGui import QMainWindow, QApplication
from PyQt4.QtCore import QTextCodec, Qt, QFile, QLatin1String, SIGNAL, pyqtSlot


QTextCodec.setCodecForTr(QTextCodec.codecForName('u8'))


import settings
if settings.DEBUG:
    # 调试的时候每次都转换一下qrc和ui文件
    import gen
    gen.run()

    # 开启js调试[相当于chrome的审查元素]
    from PyQt4 import QtWebKit
    s = QtWebKit.QWebSettings
    s.globalSettings().setAttribute(s.DeveloperExtrasEnabled, True)


import window


class MainWindow(QMainWindow, window.Ui_main_window):
    def __init__(self, app, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.app = app

        self.init_ui()

        # 其他ui界面的初始化工作
        import login
        # 这里必须将这个LoginHandler的实例保存起来，不然被析构掉后，槽就没有了
        self.login_handler = login.LoginHandler(self)

        import libqq
        self.coco = libqq.Coco()
        import mainpanel
        self.main_panel_handler = mainpanel.MainHandler(self)

        self.init_event()
        self.init_connect()

        # 长连接
        import thread
        thread.start_new_thread(self.poll, ())
        # 心跳
        thread.start_new_thread(self.coco.get_msg_tip, ())

        import os.path as osp
        if not osp.exists(settings.DB_FILE_PATH):
            import models
            models.init_db()
            # 调试用
            self.login_btn.click()
        else:
            self.login_input_qq.setText('')
            self.login_input_pwd.setText('')

    @pyqtSlot()
    def webkit_enter_key_pressed(self):
        '''在输入编辑器中用户按下回车[表示发送消息]'''
        self.send_btn.click()

    def poll(self):
        import time
        coco = self.coco
        while 1:
            try:
                time.sleep(1)
                if not hasattr(self.main_panel_handler, 'root'):
                    continue
                ret = coco.poll().next()
                type_ = ret['msg']
                if type_ == coco.MESSAGE:
                    self.main_panel_handler.new_friend_msg(ret['data'])
                elif type_ == coco.UPDATE_STATUS:
                    pass
                elif type_ == coco.FORCE_OFFLINE:
                    pass
            except StopIteration:
                pass

    def init_ui(self):
        self.load_stylesheet()

        '''
        # 加载字体
        from PyQt4.QtGui import QFontDatabase
        f = QFile(':/font/yy.otf')
        f.open(QFile.ReadOnly)
        QFontDatabase.addApplicationFontFromData(f.readAll())
        f.close()
        self.setStyleSheet(
            QString.fromUtf8('font: 12pt "造字工房悦圆演示版";'))
        '''

        # 无标题栏，置顶
        #self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.root_widget.layout().setContentsMargins(0, 0, 0, 0)

        # 只显示登录窗口
        self.main_widget.hide()
        self.login_loading_area.hide()
        if not settings.DEBUG:
            self.background_view.hide()

        self.nick.setText('')
        self.center_splitter.setStretchFactor(0, 2)
        self.center_splitter.setStretchFactor(1, 1)

    def init_connect(self):
        # 登录成功后
        self.connect(
            self, SIGNAL('login success'), self.main_panel_handler.init_ui)

    def init_event(self):
        pass

    def load_stylesheet(self):
        f = QFile(':/style.css')
        f.open(QFile.ReadOnly)
        stylesheet = QLatin1String(f.readAll())
        f.close()
        self.app.setStyleSheet(stylesheet)

    def set_fixed_size(self, w, h):
        '''将窗口设置为固定大小'''
        self.setMinimumSize(w, h)
        self.setMaximumSize(w, h)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow(app)
    main.show()
    app.exec_()
