import traceback
from handlers import ApiHandler, SecureCookie
import q
from common.mongodb import DBS
import time
import hashlib
import hmac
import uuid
import config

collection = DBS["db_test"]["user"]


def create_signature(text):
    sha256 = hmac.new(config.security_settings["hash_salt"], digestmod=hashlib.sha256)
    sha256.update(text.encode("utf8"))
    return sha256.hexdigest()


async def login(req_data):

    signature = create_signature("%s\x00%s" % (req_data["username"], req_data["password"]))
    db_query = {
        "username": req_data["username"],
        "signature": signature,
        "status": 1,
    }

    res = await collection.find_one(db_query, {"_id": 0, "signature": 0})
    assert res, "username or password not match"

    return res, 1


async def query(req_data):

    db_query = {"username": req_data["username"]}
    res = await collection.find_one(db_query, {"_id": 0, "signature": 0})

    return res, 1


async def content_author(req, paras, templete_name):

    req_data = {
        "username": paras[0],
    }

    res, _ = await query(req_data)
    if not res:
        return {}

    format_res = {("%s.%s" % (templete_name, x)): res[x] for x in res}
    return format_res


async def register(req_data):

    db_query = {"username": req_data["username"]}
    exists_user = await collection.find_one(db_query, {"_id": 1})
    assert not exists_user, "username %s already exists" % (req_data["username"])

    signature = create_signature("%s\x00%s" % (req_data["username"], req_data["password"]))
    db_data = {
        "username": req_data["username"],
        "signature": signature,
        "status": 1,
    }
    await collection.insert_one(db_data)

    return req_data["username"], 1


class LoginHandler(ApiHandler):

    @classmethod
    async def do(cls, req):

        res_data = cls._res_json.copy()
        req_json = await cls._prepare_request_json(req)

        try:
            user_info, _ = await login(req_json)
            res_data.update({
                "data": user_info,
                "rows": 1,
            })
        except Exception:
            print(traceback.format_exc(), flush=True)
            res_data.update({
                "code": cls._error_code,
                "desc": "Access info not exists",
            })

        # 返回 json 信息，并设置 cookie
        try:
            resp = cls._send_response(res_data)
            if res_data["code"] == cls._good_code:
                SecureCookie.set_cookie(resp, "access_code", "ayiis")
            return resp
        except Exception:
            print(traceback.format_exc(), flush=True)
