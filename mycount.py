#!/usr/bin/env python
# coding:utf-8
import re
import os

logfile = '/home/fengxu/log.sql'

reg = re.compile("^values\s+\('\w+','(\w+)'")

sessions = set([])

with open(logfile) as f:
    for line in f:
        match = reg.match(line)
        if match:
            sessions.add(match.group(1))

print sessions
print len(sessions)


def main():
    pass


if __name__ == '__main__':
    main()
