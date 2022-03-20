#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
# @Time    : 2021/3/25 23:53
# @Author  : 超级无敌张铁柱
# @File    : MySwitch.py
# !/usr/bin/python3.6
# -*- coding: utf-8 -*-
# @Time    : 2021/3/25 23:53
# @Author  : 超级无敌张铁柱
# @File    : switch.py
# !/usr/bin/python3.6
# -*- coding: utf-8 -*-
# @Time    : 2021/3/25 23:53
# @Author  : 超级无敌张铁柱
# @File    : switch.py
#
# from SSHConnection import ssh_client
#
# ip = '192.168.56.33'
# name = 'client001'
# password = 'Huawei@1234'
# ibc_name = 'ibc_os_hs'
# waitstr_admin = ']'
# waitstr_ibc = 'diagnose'
#
# switch = ssh_client()
# switch.create_client(ip=ip, name=name, password=password)
# cmd1 = 'system-view'
# cmd2 = 'display vlan summary | no-more'
# cmd3 = 'display vlan | no-more'
# a = switch.execCommand(cmd='system-view', waitstr=']')
# d = switch.execCommand(cmd=cmd2, waitstr=r'\[~HUAWEI\]')
# # e = switch.execCommand(cmd=cmd3, waitstr='---- More ----|]')
# print(d)
# d = """
# Number of static VLAN: 137
# VLAN ID: 1 3 5 to 6 60 to 100 103 to 155 180 183
#          to 190 200 210 to 220 230 240 244
#          to 250 252 254 256 258 260 262 264 266
#          268
#
# Number of dynamic VLAN: 0
# VLAN ID:
#
# Number of service VLAN: 4
# VLAN ID: 4091 to 4094
#
# """


#         all_summary = """
#         [~HUAWEI]display vlan summary
# Number of static VLAN: 19
# VLAN ID: 1 to 2 4 6 8 10 12 to 16 18 to 22 24
#          to 26
#
# Number of dynamic VLAN: 0
# VLAN ID:
#
# Number of service VLAN: 4
#
#         """


import re
import socket
import time

import paramiko

ip = '192.168.56.3'
name = 'client001'
password = 'Huawei@1234'
ibc_name = 'ibc_os_hs'
waitstr_admin = ']'
waitstr_ibc = 'diagnose'


# def get_switch_all_vlan(content):
#     vlan_id_pattern = r'(?ms)(?<=VLAN ID: ).+(?=\n\nNumber of dynamic)'
#     result = re.search(vlan_id_pattern, content).group()
#     # print(result, 1111111111111111)
#     # vlan_pattern = r'(?ms).+\d'
#     # result = re.search(vlan_pattern, content)
#     return result
#
# print('=====================================')
# result = get_switch_all_vlan(content=d)
# print(result, 222222222222222)
# print('=====================================')
# res = result.split('\n')
# print(res)
# print('=====================================')
# for item in range(len(res)):
#     print(item)
#     res[item] = res[item].lstrip()
#     res[item] = res[item].rstrip()
# print(res)
# result = ' '.join(res)
# print(result)

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
        # 进去交换机视图
        result_list = []
        into_system_view = {'command': ['system-view'], 'waitstr': ']'}
        self.run(into_system_view)

        # 获取交换机VLAN概括
        search_all_summary = {'command': ['display vlan summary | no-more'], 'waitstr': ']'}
        all_summary = self.run(search_all_summary)  # 这里注意拿回显
        # print('VLAN 的概述......................', all_summary)

        # 获取交换机总共配置了多少VLAN
        get_vlan_number = r'Number of static VLAN: (?P<number>\d+)'
        number = re.search(get_vlan_number, all_summary).groupdict('number')['number']
        # print('VLAN 数量 %s .....................' % number)

        # 如果交换机只有一个VLAN,说明只有默认VLAN 1
        if number == '1':
            result_list.append(number)
            return result_list

        # 如果VLAN不止一个, 剔除服务、动态VLAN描述字符，获取目标VLAN描述
        find_target_summary = r'(?ms)(?<=VLAN ID: ).+(?=\r\nNumber of dynamic|\nNumber of dynamic)'
        target_summary = re.search(find_target_summary, all_summary)
        if not target_summary:
            return result_list
        target_summary = target_summary.group()

        # 提取目标VLAN字符（中间含有to 表示范围， 还有空格 换行）
        filter_pattern = r'(?ms).+\d'
        filter_result = re.search(filter_pattern,
                                  target_summary).group()  # '1 3 100 to 200 300 302 304 306 308 310\r\n\r\n312 314 316 318 400 to 403'

        # 处理换行和空格
        result_info = re.split(r'\r\n|\n',
                               filter_result)  # ['1 3 100 to 200 300 302 304 306 308 310 ', '         312 314 316 318 400 to 403']
        for i in range(len(result_info)):
            result_info[i] = result_info[i].lstrip()
            result_info[i] = result_info[i].rstrip()

        temp_result = ' '.join(result_info)  # 1 3 100 to 200 300 302 304 306 308 310 312 314 316 318 400 to 403
        print('去除左右空格后拼接的结果...................', temp_result)

        pattern = r'(?P<start>\d+) to (?P<end>\d+)'
        number_to_number: list = re.findall(pattern, temp_result)
        print('查询 带 to 的区间vlan', number_to_number)
        if number_to_number:
            for item in number_to_number:
                for i in range(int(item[0]), int(item[1]) + 1):
                    result_list.append(str(i))
        temp_result = temp_result.split('to')  # 去除字符中的to,变成一个列表, ['1 5 ', ' 100']
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

    def get_interface_info(self, interface:str):
        """

        :param interface:
        :return:
        """
        # result = {'type_link': None, 'pvid': None, 'allow_pass': None, 'untagged_vlan': None, 'tagged_vlan': None}
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

        if interface_type.lower() == 'hybrid':
            tagged_vl = []
            untagged_vl = []
            result.update(type_link='hybrid')
            pvid_result = re.search(pvid_pattern, interface_info)
            if not pvid_result:
                result.update(pvid='1')
            else:
                result.update(pvid=pvid_result.groupdict().get('pvid'))

            tagged_result: list = re.findall(tagged_vlan_pattern,
                                             interface_info)
            untagged_result: list = re.findall(untagged_vlan_pattern,
                                               interface_info)

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
            'to')
        for i in range(len(target_result_list)):
            target_result_list[i] = target_result_list[i].lstrip()
            target_result_list[i] = target_result_list[i].rstrip()

        temp_list = ' '.join(target_result_list).split(' ')
        for j in temp_list:
            if j in result:
                continue
            result.append(j)
        return result

    def into_view(self):
        """
        进入操作视图
        :return: boolean
        """
        into_system_view = {'command': ['system-view'], 'waitstr': ']'}
        into_view_echo = self.run(into_system_view)     # 🔺注意拿回显
        cmd_correct_pattern = r'Enter system view, return user view with return command'
        if re.search(cmd_correct_pattern, into_view_echo):
            return True

        cmd_failed_pattern = r'\[\*'
        if re.search(cmd_failed_pattern, into_view_echo):
            # return_user_view = {'command': ['return'], 'input': ['yes', '>'],
            #                     'waitstr': r']|\[Y\(yes\)/N\(no\)/C\(cancel\)\]'}
            return_user_view = {'command': ['return'], 'waitstr': r'\[Y\(yes\)/N\(no\)/C\(cancel\)\]'}
            confirm = {'command': ['no'], 'waitstr': '>'}
            self.run(return_user_view)
            self.run(confirm)
            into_view_echo = self.run(into_system_view)     # 🔺注意拿回显
            if re.search(cmd_correct_pattern, into_view_echo):
                return True
            return False

        return_user_view = {'command': ['return'], 'waitstr': '>'}
        self.run(return_user_view)
        into_view_echo = self.run(into_system_view)     # 🔺注意拿回显
        if re.search(cmd_correct_pattern, into_view_echo):
            return True
        return False

    def modify_interface_type(self, interface_number: str, interface_type: str):
        """
        修改交换机接口类型
        :param interface_number: 交换机接口号
        :param interface_type: 交换机类型
        :return: boolean
        """
        if interface_type not in ['access', 'trunk', 'hybrid']:
            raise (TypeError, '接口类型必须是access trunk hybrid,实际接收到的类型为:',  interface_type)
        self.into_view()
        into_interface = {'command': ['interface %s' % interface_number], 'waitstr': ']'}
        self.run(into_interface)

        init_interface = {'command': ['port link-type %s' % interface_type], 'waitstr': ']'}
        self.run(init_interface)

        commit = {'command': ['commit'], 'waitstr': ']'}
        self.run(commit)

        display_this = {'command': ['display this'], 'waitstr': ']'}
        interface_summary = self.run(display_this)          # 🔺注意拿回显
        pattern = r'link-type %s' % interface_type
        if re.search(pattern, interface_summary):
            return True
        return False

    def create_vl(self, vl: int):
        """
        创建VLAN
        :param vl: vlan id, vlan有效范围1-4094)
        :return: boolean
        """
        if not isinstance(vl, int):
            raise (TypeError, 'vl类型错误,请输入1-4094范围内整数')
        if vl > 4094 or vl < 1:
            raise (TypeError, 'vl数值错误,请输入1-4094范围内整数')
        vl = str(vl)
        self.into_view()
        create_vl_cmd = {'command': ['vlan batch %s' % vl], 'waitstr': ']'}
        self.run(create_vl_cmd)
        all_vl = self.get_switch_all_vlan()
        if vl in all_vl:
            return True
        return False

    def delete_vl(self, vl:int):
        """
        删除VLAN
        :param vl:
        :return:
        """
        if not isinstance(vl, int):
            raise (TypeError, 'vl类型错误,请输入1-4094范围内整数')
        if vl > 4094 or vl < 1:
            raise (TypeError, 'vl数值错误,请输入1-4094范围内整数')
        delete_vl_cmd = {'command': ['undo vlan batch %s' % vl], 'waitstr': ']'}
        self.run(delete_vl_cmd)
        all_vl = self.get_switch_all_vlan()
        if vl in all_vl:
            return False
        return True



# a = '[Y(yes)/N(no)/C(cancel)]'

client = BaseCase()
# temp3 = client.get_interface_info('GE1/0/20')
# print(temp3)

# print(client.modify_interface_type('GE1/0/10', '1'))
# print(client.modify_interface_type('GE1/0/11', '2'))
# print(client.into_view())
# print(client.into_view())
a = client.create_vl()
print(a)