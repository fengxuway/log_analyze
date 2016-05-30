# -*- coding: UTF-8 -*-
__author__ = 'fengxu'
import MySQLdb
import myconfig as config
from contextlib import contextmanager
import traceback

host = config.get("host")
user = config.get("username")
port = int(config.get("port"))
passwd = config.get("password")
db = config.get("dbname")
charset = "utf8"


@contextmanager
def connect():
    """Mysql Connect Util, use 'with' to execute sqls"""
    conn = None
    try:
        conn = MySQLdb.connect(
            host=host,
            user=user,
            port=port,
            passwd=passwd,
            db=db,
            charset=charset)
    except Exception, e:
        raise Exception("Database Connect Failed! Please check database.ini.")
    cursor = conn.cursor()
    try:
        yield cursor
        cursor.close()
        conn.commit()
    except Exception, e:
        try:
            cursor.close()
        except:
            pass
        try:
            print "Rollback!!!!!!!!!!!!!!!!!!!!!!"
            conn.rollback()
        except:
            pass
        traceback.print_exc()
    finally:
        try:
            conn.close()
        except:
            pass

