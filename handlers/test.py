import time
from common.mongodb import DBS

collection = DBS["db_test"]["c_test"]


async def do(req_data):
    print("req_data: %s" % (req_data), flush=True)
    print("Got id: %s" % (req_data["id"]))

    req_data["_datetime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    await collection.insert_one(req_data)
    print("Data in mongodb: %s" % (await collection.count_documents({})))

    return {"whoami": "www"}
