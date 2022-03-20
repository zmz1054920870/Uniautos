#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
# @Time    : 2022/3/09 14:53
# @Author  : 张铁柱
# @File    : switch.py
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
        result = self.recv(waitstr, nbytes, timeout, lastSendData=cmd)
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
        command = cmdSpec.get('command')[0]
        waitstr = cmdSpec.get('waitstr')
        # print(command, waitstr)
        result = self.execCommand(cmd=command, waitstr=waitstr)
        return result


class BaseCase(object):

    def __init__(self):
        self.switch = ssh_client()
        self.switch.create_client(ip=ip, name=name, password=password)
        self.run = self.switch.run

    def get_switch_all_vlan(self):
        result_list = []
        into_system_view = {'command': ['system-view'], 'waitstr': ']'}
        self.run(into_system_view)
        search_all_summary = {'command': ['display vlan summary | no-more'], 'waitstr': ']'}
        all_summary = self.run(search_all_summary)
        get_vlan_number = r'Number of static VLAN: (?P<number>\d+)'
        number = re.search(get_vlan_number, all_summary).groupdict('number')['number']
        if number == '1':
            result_list.append(number)
            return result_list
        find_target_summary = r'(?ms)(?<=VLAN ID: ).+(?=\r\nNumber of dynamic|\nNumber of dynamic)'
        target_summary = re.search(find_target_summary, all_summary)
        if not target_summary:
            return result_list
        target_summary = target_summary.group()
        filter_pattern = r'(?ms).+\d'
        filter_result = re.search(filter_pattern,
                                  target_summary).group()
        result_info = re.split(r'\r\n|\n',
                               filter_result)
        for i in range(len(result_info)):
            result_info[i] = result_info[i].lstrip()
            result_info[i] = result_info[i].rstrip()

        temp_result = ' '.join(result_info)
        print('去除左右空格后拼接的结果...................', temp_result)

        pattern = r'(?P<start>\d+) to (?P<end>\d+)'
        number_to_number: list = re.findall(pattern, temp_result)
        print('查询 带 to 的区间vlan', number_to_number)
        if number_to_number:
            for item in number_to_number:
                for i in range(int(item[0]), int(item[1]) + 1):
                    result_list.append(str(i))
        temp_result = temp_result.split('to')
        print(temp_result, 2222222222)
        for i in range(len(temp_result)):
            temp_result[i] = temp_result[i].lstrip()
            temp_result[i] = temp_result[i].rstrip()
        print(temp_result)
        splice = ' '.join(temp_result).split(' ')
        for vlan in splice:
            if vlan in result_list:
                continue
            result_list.append(vlan)
        print(result_list)
        return result_list

    def modify_interface_type(self, interface):
        """

        :param interface: 要修改的交换机端口
        :param target_type: 修改成哪种类型
        :return:
        """
        into_system_view = {'command': ['system-view'], 'waitstr': ']'}
        self.run(into_system_view)
        into_interface = {'command': ['interface %s' % interface], 'waitstr': ']'}
        self.run(into_interface)
        get_interface_information = {'command': ['display this'], 'waitstr': ']'}
        res = self.run(get_interface_information)
        untagged_vlan = r'allow-pass vlan (?P<tagged>.+\d)'
        res2 = re.findall(untagged_vlan, res)

        return res2

    def get_interface_info(self, interface):
        """

        :param interface:
        :return:
        """
        result = {}
        into_system_view = {'command': ['system-view'], 'waitstr': ']'}
        self.run(into_system_view)
        into_interface = {'command': ['interface %s' % interface], 'waitstr': ']'}
        self.run(into_interface)
        get_interface_information = {'command': ['display this'], 'waitstr': ']'}
        interface_info = self.run(get_interface_information)
        print(interface_info)
        type_pattern = r'link-type (?P<link_type>\w+)'
        default_pattern = r'default vlan (?P<pvid>\d+)'
        pvid_pattern = r'pvid vlan (?P<pvid>\d+)'
        allow_pass_pattern = r'allow-pass vlan (?P<allow>.+\d)'
        untagged_vlan_pattern = r'untagged vlan (?P<untagged>.+)'
        tagged_vlan_pattern = r'tagged vlan (?P<tagged>.+)'
        vlan_range_pattern = r'(?P<start>\d+) to (?P<end>\d+)'
        type_result = re.search(type_pattern, interface_info)

        if not type_result:
            result.update(type_link='access')
            pvid_result = re.search(default_pattern, interface_info)

            if not pvid_result:
                result.update(pvid='1')
                return result
            result.update(pvid=pvid_result.groupdict().get('pvid'))
            return result

        interface_type = type_result.groupdict().get('link_type')

        if interface_type.lower() == 'access':
            result.update(type_link='access')
            pvid_result = re.search(default_pattern, interface_info)

            if not pvid_result:
                result.update(pvid='1')
                return result
            result.update(pvid=pvid_result.groupdict().get('pvid'))
            return result

        if interface_type.lower() == 'trunk':
            allow_pass = []
            result.update(type_link='trunk')
            pvid_result = re.search(pvid_pattern, interface_info)
            if not pvid_result:
                result.update(pvid='1')
            else:
                result.update(pvid=pvid_result.groupdict().get('pvid'))

            allow_pass_result: list = re.findall(allow_pass_pattern,
                                                 interface_info)
            if not allow_pass_result:
                result.update(allow_pass=allow_pass)
                return result

            allow_pass_str: str = ' '.join(
                allow_pass_result)
            number_to_number: list = re.findall(vlan_range_pattern, allow_pass_str)
            if number_to_number:
                for item in number_to_number:
                    for i in range(int(item[0]), int(item[1]) + 1):
                        allow_pass.append(str(i))
            allow_pass_list = allow_pass_str.split(
                'to')
            for i in range(len(allow_pass_list)):
                allow_pass_list[i] = allow_pass_list[i].lstrip()
                allow_pass_list[i] = allow_pass_list[i].rstrip()
            temp_list = ' '.join(allow_pass_list).split(' ')
            for j in temp_list:
                if j in allow_pass:
                    continue
                allow_pass.append(j)
            result.update(allow_pass=allow_pass)
            return result

    @staticmethod
    def __deal_switch_summary(params: list):
        pattern = r'(?P<start>\d+) to (?P<end>\d+)'
        result = []
        match_target_result_str = ' '.join(params)
        number_to_number: list = re.findall(pattern, match_target_result_str)
        if number_to_number:
            for item in number_to_number:
                for i in range(int(item[0]), int(item[1]) + 1):
                    result.append(str(i))
        target_result_list = match_target_result_str.split(
            'to')  # # ['6 8 10 12 14 16 18 20 22 24 26 100 ', ' 102 104 ', ' 106 ']
        for i in range(len(target_result_list)):
            target_result_list[i] = target_result_list[i].lstrip()
            target_result_list[i] = target_result_list[i].rstrip()

        temp_list = ' '.join(target_result_list).split(' ')
        # print(temp_list)
        for j in temp_list:
            if j in result:
                continue
            result.append(j)
        return result


client = BaseCase()
# temp = client.get_switch_all_vlan()
# print('结果', temp)
# temp2 = client.modify_interface_type('GE1/0/6', 1)
# print('结果2', temp2)
temp3 = client.get_interface_info('GE1/0/7')
print(temp3)
# a = ['6 8 10 12 14 16 18 20 22 24', '26 100 to 102 104 to 106 108 to 110 1000 to 1002 1004 to 1006 1008 1010 1020 1030']
# a = ['1 2 3 to 4']

# c = client.deal_switch_summary(a)
# print(c)