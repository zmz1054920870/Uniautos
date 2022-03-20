#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
# @Time    : 2021/3/25 23:53
# @Author  : 超级无敌张铁柱
# @File    : conversation.py
import base64

def read_data(filename):
    pass


def convert_to_hex(filename, hex_filename):
    with open(filename, mode='rb+') as file:
        content = file.read()
    print(content)
    result = base64.b64encode(content)
    result = result.hex()
    print(result)



if __name__ == '__main__':
    filename = r'D:\id_rsa_1024.pub'
    hex_filename = r'D:\hex_rsa.pub'
    convert_to_hex(filename, hex_filename)