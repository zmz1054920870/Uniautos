#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
# @Time    : 2022/3/13 16:53
# @Author  : 张铁柱
# @File    : snetconf.py
from ncclient import manager


conn = manager.connect(host="192.168.56.3", port=22,
                       username="client001", password="Huawei@1234",
                       hostkey_verify=False,
                       device_params={'name': 'huawei'},
                       allow_agent=False,
                       look_for_keys=False)
message = '''<ifm xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
                  <interfaces>
                      <interface>
                          <ifName/>
                          <ifDynamicInfo>
                              <ifPhyStatus/>
                              <ifLinkStatus/>
                          </ifDynamicInfo>
                      </interface>
                  </interfaces>
              </ifm>'''
print(11111111111111111111)
# get调用
ret = conn.get(("subtree", message))
# 打印返回的信息
print(ret)














# with manager.connect(
#     host="192.168.56.33",
#     port=22,
#     username="client001",
#     hostkey_verify=True,
#     key_filename="private.ppk",
#     device_params={'name':'huawei'}) as m:
#     c = m.get_config(source='running').data_xml
#     with open("%s.xml" % "192.168.56.33", 'w') as f:
#         f.write(c)