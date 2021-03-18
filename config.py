import time

mongodb_settings = {
    "db_test": {
        "HOST": "127.0.0.1",
        "PORT": 27017,
        "DATABASE_NAME": "test",
        "USERNAME": "",
        "PASSWORD": "",
    }
}

system_settings = {
    "listening_port": 8888,
}

security_settings = {

    "login_url": "/login",      # 用户登陆地址
    "hash_salt": b"9f9c5a4a9707704fe3872493c229a6ba",    # 用于 md5 加密，用于保护用户信息，请务必妥善保管

    # 仅作用于 权限页面，限制浏览器
    "enable_ua": True,
    "ua": "|".join([
        r"^Mozilla/5.0 \(Macintosh; Intel Mac OS X [0-9_]+\) AppleWebKit/[0-9.]+ \(KHTML, like Gecko\) Chrome/[0-9.]+ Safari/[0-9.]+$",
        r"^Mozilla/5.0 \(Windows NT 6.1; Win64; x64\) AppleWebKit/[0-9.]+ \(KHTML, like Gecko\) Chrome/[0-9.]+ Safari/[0-9.]+$",
    ]),
}

site_variables = {
    "ts": int(time.time()),
    # "site": "https://wodove.com/",
    "site": "http://127.0.0.1:7002/",
    "site_title": "Things go wrong",
    "site_sub_title": "&nbsp;yet another one try to make them right",
    "author": "ayiis",
    "copyright": "ayiis",
}
