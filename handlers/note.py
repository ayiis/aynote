import q
import time
from common.mongodb import DBS
from common.mongodb import Helper
import uuid

collection = DBS["db_test"]["note"]


async def query(req_data):
    print("req_data: %s" % (req_data))
    print("Got note_id: %s" % (req_data["note_id"]))

    res = await collection.find_one({
        "note_id": int(req_data["note_id"]),
    }, {"_id": 0})

    return res, 1


async def add(req_data):
    print("req_data: %s" % (req_data))

    note_id = await DBS["db_test"].get_next_sequence("note")
    if note_id == 0:
        note_id = await DBS["db_test"].get_next_sequence("note")

    insert_data = {
        "note_id": note_id,
        "title": req_data.get("title") or note_id,
        "link": "/note/%s/%s" % (note_id, req_data.get("link") or note_id),
        "datetime": req_data.get("datetime") or time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
        "author": req_data.get("author") or "ayiis",
        "tags": req_data.get("tags") or "",
        "desc": req_data.get("desc") or "",
        "content": req_data.get("content") or "",
        "status": req_data.get("status") or 0,
    }

    await collection.insert_one(insert_data)
    return note_id, 1


async def edit(req_data):
    print("req_data: %s" % (req_data))

    note_id = int(req_data["note_id"])

    update_data = {
        "title": req_data.get("title") or note_id,
        "link": "/note/%s/%s" % (note_id, req_data.get("link") or note_id),
        "datetime": req_data.get("datetime") or time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
        "author": req_data.get("author") or "ayiis",
        "tags": req_data.get("tags") or "",
        "desc": req_data.get("desc") or "",
        "content": req_data.get("content") or "",
        "status": req_data.get("status") or 0,
    }

    await collection.update_one({
        "note_id": note_id
    }, {
        "$set": update_data
    })
    return note_id, 1


async def read_rank(req_data):

    note_list = await collection.find(
        {"status": 1},
        {"_id": 0, "title": 1, "link": 1}
    ).sort([("read_rank", -1), ("datetime", -1)]).limit(10).to_list(length=None)

    return note_list, 1


async def note_list(req_data):

    db_query = {"status": 1}
    db_query_extra = {"_id": 0, "title": 1, "link": 1, "author": 1, "desc": 1, "datetime": 1}
    page_query = {
        "sort_by": req_data.get("sort_by", "_id"),
        "sort_asc": req_data.get("sort_asc", -1),
        "page_index": req_data.get("page_index", 1) - 1,
        "page_size": req_data.get("page_size", 10),
    }

    res_list, res_count = await Helper.db_query_for_pages(collection, db_query, page_query, db_query_extra)

    return res_list, res_count
