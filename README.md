coco
====

**如果你在下面的哪个文件中发现了QQ号码和密码，可能是由于我的疏忽将其提交上来了，希望好心人提醒一下，感激不尽。**

![](https://github.com/Shu-Ji/coco/raw/master/doc/ss.png)

开发环境:

    * Linux pc 3.5.0-27-generic #46~precise1-Ubuntu SMP Tue Mar 26 19:33:56 UTC 2013 i686 i686 i386 GNU/Linux 
    * Python 2.7.3
    * Qt 5.0.1
    * Qt Designer 4.8.1
    * PyQy-x11-gpl-4.10.1
    * sqlalchemy 0.8
    * jinja2 2.6

使用需自行搭建环境，代码只要程序根目录下的所有py文件，data目录，其他文件均可删
除.


目录结构说明:

├── analyze  # 分析webqq协议时候用到的一些东西
│   ├── analyze.rst  # 分析说明
│   ├── friends_list  # 好友列表返回数据
│   └── online_list  # 在线列表数据
├── data  用来存放用户数据的目录
│   └── cocoqq.db  数据库[历史记录等]
├── doc  # 文档
│   └── ss.png
├── gen.py  # 将Qt Designer产生的ui文件和qrc文件转换成python代码
├── libqq.py  # webqq协议的python实现版本[可单独作为其他程序引用]
├── login.py  # 登录面板操作功能
├── magic.py  # 判断用户图片类型的库
├── mainpanel.py  # 所有聊天时的操作都在这里
├── main.py  # 入口文件 python main.py可启动程序
├── models.py  # 数据库表结构[sqlalchemy]
├── net.py  # 为libqq.py提供基本的GET和POST方法[带cookie并模拟成chrome]
├── README.md  # 本文件
├── res  # 开发时用的资源文件全部在这里
│   ├── font  # 字体文件
│   │   └── yy.otf
│   ├── img  # 所有的图片都在这里
│   │   ├── face.gif
│   │   ├── faces  # 表情图片
│   │   │   ├── 0.gif
│   │   │   └── .....
│   │   └── ..........
│   ├── rsrc.qrc  # Qt Designer产生的qrc文件
│   ├── snd  # 声音文件
│   │   ├── audio.ogg  # tm的声音[程序默认]
│   │   ├── classic  # 普通qq的声音
│   │   │   ├── shake.ogg
│   │   │   └── ........
│   │   └── .............
│   ├── static  # 静态文件
│   │   ├── css
│   │   │   └── body.css  # 聊天信息显示css
│   │   └── js
│   │       ├── background.js  # 后台一些操作[比如播放声音等等]
│   │       ├── body.js  # 聊天信息显示区域
│   │       ├── editor.js  # 输入框[消息发送框]
│   │       ├── jquery.js
│   │       └── jquery.timeago.js  # 此插件暂时没用
│   ├── style.css  # 界面css文件
│   ├── template  # 模板目录
│   │   ├── background.html  # 后台
│   │   ├── body.html  # 消息显示
│   │   └── editor.html  # 消息输入框
│   └── window.ui  # Qt Designer设计文件
├── rsrc_rc.py  # qrc文件转换后的py代码
├── settings.py  # 一些设置
├── template.py  # 封装的一个jinja2模板操作接口
├── utils.py  # 一些通用工具
└── window.py  # ui文件转换后的python代码
