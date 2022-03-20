#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
# @Time    : 2021/3/25 23:53
# @Author  : 超级无敌张铁柱
# @File    : swtich.py
#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
# @Time    : 2021/3/25 23:53
# @Author  : 超级无敌张铁柱
# @File    : SSHConnection.py
import paramiko
import time
import socket
import re

ip = '192.168.56.33'
name = 'client001'
password = 'Huawei@1234'
ibc_name = 'ibc_os_hs'
waitstr_admin = ']'
waitstr_ibc = 'diagnose'


class ssh_client(object):

    def __init__(self):
        self.channel = None
        self.linesep = '\n'

    def create_client(self, ip, name, password):
        t = paramiko.Transport(ip, 22)  # 设置ssh连接的远程主机地址和端口
        t.connect(username=name, password=password)
        channel = t.open_session()  # 连接成功后打开一个channel
        channel.get_pty(width=200, height=200)  # 打开远程的terminat
        channel.invoke_shell()
        channel.settimeout(10)
        self.channel = channel

    def execCommand(self, cmd, waitstr='[>#]', timeout=120, nbytes=32768):
        if not self.send(cmd, timeout=timeout):  # 命令发送成功，等待回显
            return None
        result= self.recv(waitstr, nbytes, timeout, lastSendData=cmd)
        return result

    def send(self, cmd, timeout=120):
        nowTime = time.time()
        endTime = nowTime + timeout
        channle = self.channel

        while nowTime < endTime:
            try:
                channle.send(cmd + self.linesep)
                return True
            except socket.timeout as e:
                print('time out')
            nowTime = time.time()
        return False

    def recv(self, waitstr='[>#]', nbytes=None, timeout=120, lastSendData=None):
        isMatch = False
        matchStr = None
        recv = ''
        channel = self.channel

        nowTime = time.time()
        endTime = nowTime + timeout

        while nowTime < endTime:
            strGet = ''
            match = None
            try:
                strGet = channel.recv(nbytes).decode('utf8')
            except socket.timeout:
                warnmsg = 'echo is not received'
                print(warnmsg)
            if strGet is not '':
                # print(strGet, 1111111111111111111111, recv)
                recv += strGet
                match = re.search(waitstr, recv)
            if match:
                isMatch = True
                matchStr = match.group()
                break
            nowTime = time.time()
        return recv

    def run(self, cmdSpec):
        command = cmdSpec.get('command')
        waitstr = cmdSpec.get('waitsr')
        result = self.execCommand(cmd=command, waitstr=waitstr)
        return result

# switch = ssh_client()
# switch.create_client(ip=ip, name=name, password=password)
# cmd1 = 'system-view'
# cmd2 = 'display vlan summary | include VLAN ID:'
# cmd3 = 'display vlan'
# a = switch.execCommand(cmd='system-view', waitstr=']')
# d = switch.execCommand(cmd=cmd2, waitstr=r'\w+')
# # e = switch.execCommand(cmd=cmd3, waitstr='---- More ----|]')
# print(d)