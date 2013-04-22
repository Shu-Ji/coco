#coding: u8

import sys

from PyQt4.QtGui import (
    QMainWindow, QApplication, QSplitter, QListWidget, QTextEdit, QTextBrowser,
    QVBoxLayout, QPushButton
)
from PyQt4.QtCore import QTextCodec, Qt


QTextCodec.setCodecForTr(QTextCodec.codecForName('u8'))


class MainWidget(QMainWindow):
    def __init__(self, app, parent=None):
        super(MainWidget, self).__init__(parent)

        self.parent = parent
        self.app = app
        self.init_ui()

    def init_ui(self):
        self.load_stylesheet()
        self.setWindowTitle('COCO')

        self.main_splitter = QSplitter(Qt.Horizontal, self)

        # 边栏
        self.sidebar = QListWidget(self.main_splitter)
        self.login_panel = QVBoxLayout(self.sidebar)
        #login_btn = QPushButton(self.login_panel)
        #login_btn.setObjectName('login-btn')

        # 主栏
        self.center_splitter = QSplitter(Qt.Vertical, self.main_splitter)
        # 显示内容区域[0]
        self.body = QTextBrowser(self.center_splitter)
        # 输入区域[1]
        self.footer = QTextEdit(self.center_splitter)
        # 设置中间分隔条的高度, [0]占据三分之二的高度
        self.center_splitter.setStretchFactor(0, 2)
        self.center_splitter.setStretchFactor(1, 1)

        # [缩放窗口时]主栏设置为自动收缩
        self.main_splitter.setSizes([220, 1])

        # 隐藏主栏，只显示登录窗口[边栏]
        self.center_splitter.hide()

        self.setObjectName('mainwindow')
        self.main_splitter.setObjectName('main-splitter')
        self.sidebar.setObjectName('sidebar')
        self.login_panel.setObjectName('login-panel')
        self.body.setObjectName('body')
        self.footer.setObjectName('footer')

        # 设置窗口大小
        d = QApplication.desktop()
        w = d.width()
        h = d.height()
        ww = 320
        wh = 4 * h / 5
        self.setMinimumSize(ww, wh)
        self.setMaximumSize(ww, wh)

        # 将窗口移动到屏幕右边
        self.move(w - w / 4, (h - self.height()) / 2)

        self.setCentralWidget(self.main_splitter)

    def set_window_size(self):
        # 获取屏幕大小
        d = QApplication.desktop()
        w = d.width()
        h = d.height()
        # 设置程序大小为屏幕的五分之四大小
        ww = 4 * w / 5
        wh = 4 * h / 5
        self.resize(ww, wh)
        self.setMinimumSize(ww, wh)
        self.setMaximumSize(w, h)

    def load_stylesheet(self):
        self.app.setStyleSheet(open('res/style.css').read())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWidget(app)
    main.show()
    app.exec_()
