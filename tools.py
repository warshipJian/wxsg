#!/usr/bin/env python
#coding:utf8

'''
基础工具
'''

import hashlib
import os
import sys
import statvfs
import requests

class md5:

    def __init__(self,value):
        self.value = value

    def get_value(self):
        m = hashlib.md5()
        m.update(self.value)
        return m.hexdigest()

class getip:

    def client(self):
        r = requests.get('http://test.abuyun.com/')
        html = r.text

        for i in html.split('\n'):
            if 'client-ip' in i:
                i = i.split('<td>')
                return i[1].strip('</td></tr>')


class fdisk:

    def status(self):
        if 'linux' not in sys.platform:
            print('sorry! system opreation not supply!')
            sys.exit(3)

        mount = []
        result = []
        label = []
        status = 0

        with open('/proc/mounts') as f:
            for v in f:
                v = v.split()
                mountName = v[1]
                if v[0]  in mount:
                    continue
                mount.append(v[0])
                try:
                    vfs=os.statvfs(mountName)
                except OSError:
                    print('mounted device error, plase check %s' % mountName)
                    sys.exit(3)
                totalSpace= vfs[statvfs.F_BLOCKS]*vfs[statvfs.F_BSIZE]/(1024*1024*1024)
                if totalSpace == 0:
                    continue
                availSpace= vfs[statvfs.F_BAVAIL]*vfs[statvfs.F_BSIZE]/(1024*1024*1024)
                availInode = vfs[statvfs.F_FFREE]
                totalInode = vfs[statvfs.F_FILES]
                usedSpace = totalSpace - availSpace
                usedInode = totalInode - availInode
                usedSpacePer = float(usedSpace)/totalSpace * 100
                usedInodePer = float(usedInode)/totalInode * 100
                usedSpacePercent = "{0:.0f}%".format(usedSpacePer)
                usedInodePercent = "{0:.0f}%".format(usedInodePer)
                if usedSpacePer >= 95 or usedInodePer >= 95:
                    status = 2
                elif usedSpacePer >= 85 or usedInodePer >= 85:
                    status = 1
                info = '%s=%sGB,%s inode=%s;' % (mountName,availSpace,usedSpacePercent,usedInodePercent)
                if info not in result:
                    result.append(info)
                    label.append('%s=%s;%s;%s;0;%s ' % (mountName,availSpace,0,availSpace*2,availSpace*4))
        #print 'free space:%s|%s' % (''.join(result),''.join(label))
        return status
