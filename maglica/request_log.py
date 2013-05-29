import os
import sqlite3
import datetime
import json


class RequestLog():

    def __init__(self):
        db_dir = "/var/lib/maglica"
        db_file = db_dir + "/maglica.db"

        con = None
        if not os.path.exists(db_file):
            try:
                os.mkdir(db_dir)
            except:
                pass
            con = sqlite3.connect(db_file)
            sql = """
            create table requests(
            id integer primary key autoincrement,
            args text,
            message text,
            status integer,
            create_on text,
            modify_on text
            );
            """
            con.execute(sql)
            con.commit()

        if not con:
            con = sqlite3.connect(db_file)

        self.con = con
        self.cur = con.cursor()
        self.con.row_factory = sqlite3.Row

    def insert_request(self, args):
        if "host" in args and "name" in args["host"]:
            args["host"] = args["host"]["name"]
        args = json.dumps(args)
        sql = """
        insert into requests ( args, create_on, modify_on, status ) values ( ?, ?, ?, ? )
        """

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%m:%S')
        self.cur.execute(sql, [args, now, now, 0])
        self.con.commit()

        return self.cur.lastrowid

    def update_status(self, request_id, status, message):
        sql = """
        update requests set status = ?, message = ? where id = ?
        """
        self.cur.execute(sql, [status, message, request_id])
        self.con.commit()

    def get_status(self, request_id):
        sql = "select * from requests where id = ?"
        row = self.con.execute(sql, [request_id]).fetchone()
        return row

    def tail(self):
        sql = "select * from requests order by id desc limit 10"
        row = self.con.execute(sql).fetchall()
        row.reverse()
        return row
