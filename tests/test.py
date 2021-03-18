import requests
import q

target_site = "http://127.0.0.1:7001"

if "测试 API 接口":

    res = requests.post("%s%s" % (target_site, "/api/test"), headers={
        "content-type": "application/json; charset=UTF-8",
    }, data="""{"id": 12345}""")

    assert res.status_code == 200, "res.code should be 200"
    assert res.json()["code"] == 0, "json.code should be 0"

    target_site = "http://127.0.0.1:7001"
    res = requests.post("%s%s" % (target_site, "/api/test2"), headers={
        "content-type": "application/json; charset=UTF-8",
    })

    assert res.status_code == 404, "res.code should be 404"


if "测试 静态文件":

    res = requests.get("%s%s" % (target_site, "/static/txt.txt"))
    assert res.status_code == 404, "res should be 404"

    res = requests.get("%s%s" % (target_site, "/static/js/js.js"))
    assert res.status_code == 200, "res should be 200"

    res = requests.get("%s%s" % (target_site, "/static/css/css.css"))
    assert res.status_code == 200, "res should be 200"

    res = requests.get("%s%s" % (target_site, "/static/img/img.img"))
    assert res.status_code == 200, "res should be 200"

    res = requests.get("%s%s" % (target_site, "/static/no_exists.txt"))
    assert res.status_code == 404, "res should be 404"

    res = requests.get("%s%s" % (target_site, "/static/../../tests/test.py"))
    assert res.status_code == 404, "res should be 404"

    pass

print("ALl check pass.")
