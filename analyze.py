#!/usr/bin/env python
# coding:utf-8
import re
from mysql_util import connect
import os
import shutil
import commands

"""
----------------------------------------
install setup tools
wget http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11-py2.7.egg#md5=fe1f997bc722265116870bc7919059ea --no-check-certificate
sh setuptools-0.6c11-py2.7.egg

----------------------------------------
install pip

wget --no-check-certificate http://pypi.python.org/packages/source/p/pip/pip-1.0.2.tar.gz
tar zxf pip-1.0.2.tar.gz
cd pip-1.0.2
python setup.py install
"""


def log_files():
    files = ['/home/fengxu/log1.log']
    return files


log_file = 'log.sql'


reg = '''.*?ERROR.*?setMsg\s+-\s+Exception\s+java.sql.SQLException:.*?at.*?/\s+(\w+)[\s/]+(\d+)[\s/]+(\w+)[\s/]+({.*?})[\s/]+(<msg.*?msgid="(\d+)".*?</msg>)'''


pattern = re.compile(reg)


def process(line):
    if line.find("SQLException") < 0:
        return None
    match = pattern.match(line)
    if match:
        return {
            "sourceid": match.group(1),
            "sessionid": match.group(3),
            "msg": match.group(5),
            "time": match.group(2),
            "srcname": match.group(4),
            "msgid": match.group(6)
        }
    return None


def check_exists(cursor, msgid):
    check_sql = 'select * from t2d_chatmessage where msg like \'%msgid="' + msgid + '"%\''
    cursor.execute(check_sql)
    if cursor.fetchone():
        return True
    return False


def catch_data():
    lst = []
    sql = """select sessionid from t2d_chatscene where success=0 """
    with connect() as cursor:
        cursor.execute(sql)
        results = cursor.fetchall()
        for i in results:
            lst.append(i[0])
    return lst


def flush_database(cursor, data):
    sql = """
insert into t2d_chatmessage
(`sourceid`,`sessionid`,`msg`,`time`,`srcname`)
values ('%s','%s','%s','%s','%s');
""" % (data['sourceid'], data['sessionid'], data['msg'], data['time'], data['srcname'])
    # cursor.execute(sql)
    print "insert: ", sql

    sql_update = """
update t2d_chatscene
set `success`=1
where `sessionid`='%s';
""" % data['sessionid']
    print "update: ", sql_update
    # cursor.execute(sql_update)
    with open(log_file, 'a') as f:
        f.write(sql + '\n')
        f.write(sql_update + '\n')


msgids = []


def main(files):
    sessionids = catch_data()
    # TODO 去重
    # for _file in log_files():
    for _file in files:
        try:
            with open(_file) as f:
                for line in f:
                    data = process(line)
                    with connect() as cursor:
                        if data and data['sessionid'] in sessionids \
                                and not check_exists(cursor, data['msgid'])\
                                and data['msgid'] not in msgids:
                            print "line: ", line
                            with open(log_file, 'a') as log:
                                log.write("#==========================================\n")
                                log.write("# " + line + '\n')
                            flush_database(cursor, data)
                            msgids.append(data['msgid'])
        except IOError:
            print "No such file: ", _file


def unzip_files():
    # log_dir = '/data/backup/2/htchat5.ntalker.com'
    log_dir = '/home/fengxu/download/kf/logs'
    os.chdir(log_dir)
    for tar in os.listdir(log_dir):
        if not os.path.isfile(tar) or not tar.endswith('tar.gz'):
            continue
        print "***************  ", tar, "  ****************"
        logfiles = []
        try:
            shutil.rmtree('log')
        except OSError:
            print "Delete log dir error."
        a, b = commands.getstatusoutput('tar -zxvf ' + tar)
        for zipfile in os.listdir('log'):
            zip = os.path.join('log', zipfile)
            dd = zip
            if os.path.isfile(zip) and zip.endswith('.zip'):
                print 'unzip and reading file: ', zip
                try:
                    shutil.rmtree('ttt')
                except OSError:
                    print "Delete TTT dir error."
                commands.getstatusoutput('unzip ' + zip + ' -d ttt')
                # zip = os.path.join(zip, 'ttt')
                dd = 'ttt'

            if os.path.isdir(dd):
                for logfile in os.listdir(dd):
                    log = os.path.join(dd, logfile)
                    if os.path.isfile(log) and log.endswith('.log'):
                        # logfiles.append(log)
                        main([log])


        log2_dir = 'dev/shm/tchat'
        if os.path.exists(log2_dir):
            for log in os.listdir(log2_dir):
                if os.path.isfile(os.path.join(log2_dir, log)) and log.endswith('.log'):
                    # logfiles.append(os.path.join(log2_dir, log))
                    main([os.path.join(log2_dir, log)])
        print logfiles


def main2():
    unzip_files()


if __name__ == '__main__':
    main2()

