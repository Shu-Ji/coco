coco
====

**如果你在下面的哪个文件中发现了QQ号码和密码，可能是由于我的疏忽将其提交上来了，希望好心人提醒一下，感激不尽。**

![](https://github.com/Shu-Ji/coco/raw/master/doc/ss.png)


独立二进制包[百度网盘下载](http://pan.baidu.com/share/link?shareid=585852&uk=3104301417), 下载完成后执行:

    $ chmod +x cocoqq.bin
    $ ./cocoqq.bin

即可启动程序。

附：

开发环境:

    *. Ubuntu 12.04.2 
    *. Python 2.7.3
    *. PyQt-x11-gpl-4.10.1 [基于Qt 5.0.1编译]
    *. sqlalchemy v0.8
    *. jinja2 v2.6
    *. Qt Designer 4.8.1
    *. pynotify


目录结构说明:

    ├── analyze  # 分析webqq协议时候用到的一些东西
    │   ├── analyze.rst  # 分析说明
    │   ├── friends_list  # 好友列表返回数据
    │   └── online_list  # 在线列表数据
    ├── doc  # 文档
    │   └── ss.png
    ├── gen.py  # 将Qt Designer产生的ui文件和qrc文件转换成python代码
    ├── libqq.py  # webqq协议的python实现版本[可单独作为其他程序引用，需要下面net.py的支持]
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

    另外存放历史记录和配置的文件放在你的家目录下面的.cocoqq.db中了[~/.cocoqq.db]
    
QQ机器人的实现：

在mainpanel.py的def new_friend_msg(self, msg)方法的结尾处对msg进行处理即可，然后返回你要自动回复的内容并调用self.send_friend_msg(uin, u'这是处理后你自动回复的内容')就可以了，稍后奉上Demo。

或者前往https://github.com/Shu-Ji/qqrobot有一个可运行的聊天机器人。

Github地址: https://github.com/Shu-Ji/coco
