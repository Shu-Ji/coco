#!/usr/bin/env python
#coding:utf-8


from jinja2 import BaseLoader


class QtResourceLoader(BaseLoader):
    '''从Qt的资源中加载模板'''
    def __init__(self, debug):
        self.debug = debug

    def get_source(self, env, tmpl):
        from PyQt4.QtCore import QFile

        if self.debug:
            # 强制重新加载模板
            path = './res/template/%s' % tmpl
            html = open(path).read()
        else:
            path = ':/template/%s' % tmpl
            f = QFile(path)
            f.open(QFile.ReadOnly)
            html = f.readAll()
            f.close()
        html = unicode(html, 'u8')
        return html, path, lambda: not self.debug


class Render:
    '''封装一个全局的模板变量'''
    def __init__(self, **kwargs):
        debug = kwargs.pop('debug', False)
        from jinja2 import Environment
        self._lookup = Environment(loader=QtResourceLoader(debug), **kwargs)

    def __call__(self, path, *args, **kwargs):
        '''提供简化的模板渲染方法，实现类实例的 ``()`` 功能.

        :param path: 模板路径，可以是相对路径，相对于__init__方法中的path.
        :type path: str.
        :param args: 传递到模板中的参数，字典形式，如 ``{'name': 'Mr. U'}`` .
        :type args: dict.
        :param kwargs: 传递到模板中的参数，以参数的形式传递.

        >>> render = Render(path)
        >>> render('home.html', {'pwd': '123'}, name='Mr. U', what='hello')
        '''

        kwargs = dict(*args, **kwargs)
        return self._lookup.get_template(path).render(**kwargs)

    def get_module(self, path):
        '''渲染某个模板中的某个macro.

        :param path: 要得到的模板的(相对)路径.
        :type path: str.

        >>> render = Render(path)
        >>> render.get_module('func.html').sayHello2Me('Hi!')

        其中func.html中可能会有如下形式的定义::

            {% macro sayHello2Me(what) %}
                <p>Hello {{ what }} </p>
            {% endmacro %}
        '''

        return self._lookup.get_template(path).module
