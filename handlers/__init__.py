#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = "ayiis"
# create on 2020/11/17
import q
import hmac
import time
import hashlib
import os
import re
import json
import traceback
from aiohttp.web import HTTPException, HTTPFound, Response, json_response
from pathlib import Path
import uuid
import base64


class AyHTTPError(HTTPException):
    def __init__(self, status_code, reason):
        self.status_code = status_code
        super(AyHTTPError, self).__init__(reason=reason)


class SecureCookie:
    """
        在此处控制 cookie 的过期时间
    """
    _expire_time = 60 * 60 * 24 * 7             # 7 天
    _salt = uuid.uuid4().hex.encode("utf8")     # 一次性 cookie 加密因子，如果服务器重启，所有的用户 cookie 都会失效
    _tss = {}                                   # 记录 cookie 过期时间

    class TimeoutException(Exception): pass
    class EmptyException(Exception): pass
    class SpoofException(Exception): pass

    @classmethod
    def create_signature(cls, text):
        sha256 = hmac.new(cls._salt, digestmod=hashlib.sha256)
        sha256.update(text.encode("utf8"))
        return sha256.hexdigest()

    @classmethod
    def get_cookie(cls, req, name):

        val_string = req.cookies.get(name)
        if not val_string:
            return None

        # 检查 SecureCookie 格式
        try:
            data, sig = val_string.split("|")
        except Exception:
            raise cls.EmptyException

        # 检查 cookie 是否存在，并检查时间
        ts = int(time.time())
        if sig not in cls._tss:
            raise cls.TimeoutException
        elif cls._tss[sig] <= ts:
            del cls._tss[sig]
            raise cls.TimeoutException
        else:
            cls._tss[sig] = ts + cls._expire_time

        # 校验 cookie 不被篡改
        cmp_sig = cls.create_signature("%s\x00%s" % (name, data))
        if cmp_sig != sig:
            raise cls.SpoofException

        # base 解码
        val = base64.b64decode(data).decode("utf8")

        return val

    @classmethod
    def set_cookie(cls, resp, name, val):

        data = base64.b64encode(val.encode("utf8")).decode("utf8")
        sig = cls.create_signature("%s\x00%s" % (name, data))
        cls._tss[sig] = int(time.time()) + cls._expire_time
        val_string = "%s|%s" % (data, sig)
        resp.set_cookie(name, val_string, secure=True, httponly=True, samesite=True)

    @classmethod
    def del_cookie(cls, resp, name):
        resp.del_cookie(name)


class Authorize:

    _authorized_url = []
    _security_settings = {}

    @classmethod
    def init(cls, security_settings, authorized_url):
        cls._security_settings = security_settings
        cls._authorized_url = "|".join((x + r"\b.*") for x in authorized_url)

    @classmethod
    def wrap(cls, func):

        def do(req):

            # 权限页面
            if re.match(cls._authorized_url, req.path, re.I):

                try:

                    # 检查 浏览器
                    if cls._security_settings["enable_ua"]:
                        ua = req.headers["User-Agent"]
                        assert re.match(cls._security_settings["ua"], ua), "bad ua: %s" % (ua)

                    # 检查 cookie
                    access_code = SecureCookie.get_cookie(req, "access_code")
                    assert access_code, "access_code is empty."

                except Exception as e:

                    print("Authorize fail:", e, type(e))
                    exc = HTTPFound(location=cls._security_settings["login_url"])

                    if type(e) == SecureCookie.TimeoutException:
                        SecureCookie.del_cookie(exc, "access_code")
                    elif type(e) == SecureCookie.EmptyException:
                        SecureCookie.del_cookie(exc, "access_code")
                    elif type(e) == SecureCookie.SpoofException:
                        SecureCookie.del_cookie(exc, "access_code")
                    else:
                        pass

                    # 🚫 BUG of aiohttp, here should be `raise` not `return`
                    # However, check https://github.com/aio-libs/aiohttp/issues/5181
                    return exc

            resp = func(req)
            return resp

        return do


class ApiHandler:
    _url_handlers = {}
    _good_code = 0
    _error_code = 500

    _res_json = {
        "code": _good_code,
        "data": None,
        "rows": 0,
        "desc": "",
    }

    @classmethod
    def add_handlers(cls, url_handler_obj):
        """
            Define the function to handle the request of certain path
        """
        cls._url_handlers.update(url_handler_obj)

    @classmethod
    async def _prepare_request_handler(cls, req):
        """
            Make sure the handler exists
        """
        handler = cls._url_handlers.get(req.path)
        if handler is None:
            raise AyHTTPError(status_code=404, reason="%s Not found" % req.path)

        return handler

    @classmethod
    async def _prepare_request_json(cls, req):
        """
            Make sure the request body is json
        """
        if re.match(r"^application/json[;]?(\s*charset=UTF-8)?$", req.headers.get("Content-Type", ""), re.I) is None:
            raise AyHTTPError(status_code=400, reason="`Content-Type` Must be `application/json; charset=utf-8`")

        try:
            json_data = await req.json()
        except Exception:
            print(traceback.format_exc())
            raise AyHTTPError(status_code=400, reason="Fail to parse request json.")

        return json_data

    @classmethod
    def _send_response(cls, res_data, status_code=200):
        """
            必须使用 return 而不是 await：object Response can't be used in 'await' expression
        """
        return json_response(res_data, status=status_code)

    @classmethod
    # @Authorize.wrap
    async def do(cls, req):
        """
            1. 确保请求是 json 格式
            2. 执行路由对应的方法，获得结果
            3. 返回 json 格式的结果
        """
        handler = await cls._prepare_request_handler(req)
        req_json = await cls._prepare_request_json(req)
        res_data = cls._res_json.copy()

        # 发送到对应的执行者执行
        try:
            data, rows = await handler(req_json)
            res_data.update({
                "data": data,
                "rows": rows,
            })
        except Exception as e:
            print(traceback.format_exc(), flush=True)
            res_data.update({
                "code": cls._error_code,
                "desc": str(e),
            })

        # 返回 json 结果
        # 必须 return 到外层
        try:
            return cls._send_response(res_data)
        except Exception:
            print(traceback.format_exc(), flush=True)


class TemplateHandler:
    """
        1. 直接将 build 好的 html 缓存在内存中
        2. 当访问的路径 + jade 可以匹配时，返回内存中的内容
        3. 简单粗暴高效，适合小型网站
        4. 模板的所有修改，重启后才能生效
        5. 其实就没有用到生成的 src 的文件了，src 只能方便参考
    """
    render_variables = r"<=%(.*?)%>"

    @classmethod
    def response_html(cls, content):
        return Response(
            body=content,
            status=200,
            content_type="text/html",
            charset="utf8",
        )

    @classmethod
    def wrap(cls, templete_path, templete, index="index", extra_args={}):

        cls.templete_path = os.path.abspath(os.path.join(os.path.abspath("."), templete_path))
        cls.templete = templete

        @Authorize.wrap
        def do(req):

            req_path = req.path

            if req_path == "/":
                req_path = "/%s" % (index)

            target_path = os.path.abspath("%s/%s.jade" % (cls.templete_path, req_path))
            if not(target_path in cls.templete and target_path.startswith(cls.templete_path) and os.path.isfile(target_path)):
                raise AyHTTPError(status_code=404, reason="%s Not found" % req_path)

            content = cls.templete[target_path]
            render_content = re.sub(cls.render_variables, lambda g: extra_args.get(g.groups()[0]) or "", content)
            return cls.response_html(render_content)

        return do


class ContentHandler(TemplateHandler):
    """
        1. 使用 build 好的 template
        2. 渲染 数据 返回
            🚫 搁置。面向静态页面应当使用 服务端渲染 markdown，复杂性大幅提高
    """
    @classmethod
    def wrap(cls, templete_path, templete, templete_name, data_handler, extra_args={}):

        cls.templete_path = "%s/%s.jade" % (os.path.abspath(os.path.join(os.path.abspath("."), templete_path)), templete_name)
        cls.templete = templete
        content = cls.templete[cls.templete_path]

        @Authorize.wrap
        async def do(req):

            _, _, *paras = req.path.split("/")

            if not paras:
                raise AyHTTPError(status_code=404, reason="%s Not found" % req.path)

            res_data = await data_handler(req, paras, templete_name)
            render_data = extra_args.copy() if extra_args else {}
            render_data.update(res_data)

            print("render_data:", render_data)
            render_content = re.sub(cls.render_variables, lambda g: render_data.get(g.groups()[0]) or "", content)
            return cls.response_html(render_content)

        return do
