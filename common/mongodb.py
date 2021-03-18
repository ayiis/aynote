from motor.motor_asyncio import AsyncIOMotorClient

DBS = {}


async def init_connection(mongodb_config):

    for db_name in mongodb_config:
        db_conf = mongodb_config[db_name]
        if db_conf.get("USERNAME") and db_conf.get("PASSWORD"):
            DBS[db_name] = AsyncIOMotorClient(
                "%s:%s" % (db_conf["HOST"], db_conf["PORT"]),
                username=db_conf["USERNAME"],
                password=db_conf["PASSWORD"],
                authSource=(db_conf.get("AUTHSOURCE") or "admin"),
                authMechanism="SCRAM-SHA-1"
            )[db_conf["DATABASE_NAME"]]
        else:
            DBS[db_name] = AsyncIOMotorClient("%s:%s" % (db_conf["HOST"], db_conf["PORT"]))[db_conf["DATABASE_NAME"]]

        setattr(
            DBS[db_name],
            "get_next_sequence",
            wrapper(DBS[db_name]),
        )

    for db in DBS.values():
        try:
            await db.get_next_sequence("sequence_counters")
        except Exception as e:
            print("Mongodb error for `%s`: %s" % (db.name, e))


def wrapper(db):

    async def get_next_sequence(sequence_name):
        """
            input a string output an increment number for this string in this db collection
        """
        doc = await db.sequence_counters.find_one_and_update(
            filter={"_id": sequence_name},
            update={"$inc": {"sequence_number": 1}},
            upsert=True
        )
        if doc is None:
            doc = {"sequence_number": 0}

        return doc["sequence_number"]

    return get_next_sequence


class Helper:

    async def db_query_for_pages(col, db_query, page_query, db_query_extra=None):
        """
            db_query = {}
            page_query = {
                "sort_by": "_id",
                "sort_asc": -1,
                "page_index": 0,
                "page_size": 25,
            }
        """
        res_count = await col.count_documents(db_query)
        res_list = await col.find(db_query, db_query_extra).sort([
            (page_query["sort_by"], page_query["sort_asc"])
        ]).skip(page_query["page_index"] * page_query["page_size"]).limit(page_query["page_size"]).to_list(length=None)

        return (res_list, res_count)


async def test():

    await init_connection({
        "db_test_pwd": {
            "HOST": "192.168.1.111",
            "PORT": 27017,
            "DATABASE_NAME": "shushu_user",
            "USERNAME": "mongoadmin",
            "PASSWORD": "sksai20200810",
            "AUTHSOURCE": "admin",
        },
        "db_test": {
            "HOST": "127.0.0.1",
            "PORT": 27017,
            "DATABASE_NAME": "test",
            "USERNAME": "",
            "PASSWORD": "",
        }
    })


if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
