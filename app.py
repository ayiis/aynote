#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = "ayiis"
# create on 2020/08/11
import asyncio
import aiohttp.web


async def main():

    # 初始化数据库
    import config
    from common import mongodb
    await mongodb.init_connection(config.mongodb_settings)

    # 初始化 jade 页面
    from common.build import JadeWork
    JadeWork.set_variables(config.site_variables)
    templete = JadeWork.build("src", "src_html")

    # 启动 web 服务
    from handlers import ApiHandler, TemplateHandler, ContentHandler, Authorize
    from handlers import note, user

    app = aiohttp.web.Application()
    ApiHandler.add_handlers({
        "/api/note/query": note.query,
        "/api/note/add": note.add,
        "/api/note/edit": note.edit,
        "/api/note/read_rank": note.read_rank,
        "/api/note/note_list": note.note_list,

        "/api/user/register": user.register,
        "/api/user/query": user.query,
    })
    Authorize.init(config.security_settings, [
        r"/api/note/add",
        r"/api/note/edit",
        r"/api/user/register",    # 不开放注册

        r"/note_edit",
        # r"/note_add",
    ])

    app.router.add_static("/static/", path="./static/", name="static")  # 静态资源 js css img (下载形式)
    app.router.add_route("POST", "/login", user.LoginHandler.do)      # LoginHandler 接口
    app.router.add_route("POST", "/api/{match:.*}", ApiHandler.wrap())      # API 接口
    app.router.add_route("GET", "/{match:.*}", TemplateHandler.wrap("src", templete, index="index"))    # html 静态页面

    await asyncio.gather(
        aiohttp.web._run_app(app, port=7002),       # 启动web服务，监听端口
    )


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
