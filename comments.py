#! /usr/bin/env python
# coding='utf-8'

'''
获取网易云音乐歌曲全部评论
Author: zhouzying
URL: https://www.zhouzying.cn
Date: 2018-09-14
Update: 2018-09-27         Add data argument.
Update: 2018-10-04         Get replied comments and add users name who shared comments.
'''

import requests
import math
import random
# pycrypto
from crypto.Cipher import AES
import codecs
import base64
import time
import json
import pymysql
import re
import UserInfo

def insert_into_mysql(userId, commentId, content, likeCount, times):
    conn = pymysql.connect(host="192.168.43.202", user="root", password="123456", database="comments", charset="utf8mb4",
                           port=3306)
    cursor = conn.cursor()
    sql = "INSERT INTO comments_info(userId, commentId, content, likeCount, times) VALUES (%s, %s, %s, %s, %s);"
    cursor.execute(sql, [userId, commentId, content, likeCount, times])
    conn.commit()
    cursor.close()
    conn.close()
# 构造函数获取歌手信息
def get_comments_json(url, data):
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9',
               'Connection': 'keep-alive',
               'Cookie': 'NMTID=00O65N_o9r-mI_o000whvkK1ObYLvUAAAF6VnS1Tg; _iuqxldmzr_=32; JSESSIONID-WYYY=WmZuAU2uZ8FtQN3wB5622DHznllIP4zYmppdK1yTvto16rGMJpMraiy8y%2FjCRrGI5kaQECwu9udZ%5ClXXJJht%2FUJW0FKTZ%2BuRF6Vi5vD%2FrgcZ4TlJpHSFi0bGHItJHjG4QvaNnoeug5n7u5M3FQa%5CoMWyY7UMauuwCwjmsAX%2BxiirKNKy%3A1624951738684; _ntes_nnid=1bfbb4069e48f09b35b0accc1546f697,1624950052056; _ntes_nuid=1bfbb4069e48f09b35b0accc1546f697; WNMCID=gtllvk.1624950052143.01.0; WEVNSM=1.0.0',
               'Host': 'music.163.com',
               'Referer': 'http://music.163.com/',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/66.0.3359.181 Safari/537.36'}

    cookie = {
        'NMTID': "NMTID=00O65N_o9r-mI_o000whvkK1ObYLvUAAAF6VnS1Tg"
    }
    try:
        r = requests.post(url, headers=headers, data=data, cookies=cookie)
        r.encoding = "utf-8"
        if r.status_code == 200:
            # 返回json格式的数据
            return r.json()

    except:
        print("爬取失败!")


# 生成16个随机字符
def generate_random_strs(length):
    string = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    # 控制次数参数i
    i = 0
    # 初始化随机字符串
    random_strs = ""
    while i < length:
        e = random.random() * len(string)
        # 向下取整
        e = math.floor(e)
        random_strs = random_strs + list(string)[e]
        i = i + 1
    return random_strs


# AES加密
def AESencrypt(msg, key):
    # 如果不是16的倍数则进行填充(paddiing)
    padding = 16 - len(msg) % 16
    # 这里使用padding对应的单字符进行填充
    msg = msg + padding * chr(padding)
    # 用来加密或者解密的初始向量(必须是16位)
    iv = '0102030405060708'

    cipher = AES.new(key.encode(), AES.MODE_CBC, iv.encode())
    # 加密后得到的是bytes类型的数据
    encryptedbytes = cipher.encrypt(msg.encode("utf-8"))
    # 使用Base64进行编码,返回byte字符串
    encodestrs = base64.b64encode(encryptedbytes)
    # 对byte字符串按utf-8进行解码
    enctext = encodestrs.decode('utf-8')

    return enctext


# RSA加密
def RSAencrypt(randomstrs, key, f):
    # 随机字符串逆序排列
    string = randomstrs[::-1]
    # 将随机字符串转换成byte类型数据
    text = bytes(string, 'utf-8')
    seckey = int(codecs.encode(text, encoding='hex'), 16) ** int(key, 16) % int(f, 16)
    return format(seckey, 'x').zfill(256)


# 获取参数
def get_params(pageNo, songId, cursor):
    # msg也可以写成msg = {"offset":"页面偏移量=(页数-1) *　20", "limit":"20"},offset和limit这两个参数必须有(js)
    # limit最大值为100,当设为100时,获取第二页时,默认前一页是20个评论,也就是说第二页最新评论有80个,有20个是第一页显示的
    # msg = '{"rid":"R_SO_4_1302938992","offset":"0","total":"True","limit":"100","csrf_token":""}'
    # 读js可以知道OFFSET在map为空的时候是 Math.abs( lastPage - nowPage - 1 )*20
    # cursor是当前页面评论的最小发布时间戳 可以从前一页请求中的cursor获得
    # 偏移量
    if (pageNo == 1):
        offset = 0
    else:
        offset = 40
    # offset和limit以及cursor是必选参数,其他参数是可选的,其他参数不影响data数据的生成
    # msg = '{"offset":' + str(offset) + ',"pageNo":"52","pageSize":"20","total":"True","limit":"20","csrf_token":"","rid":"R_SO_4_411214279","threadId":"R_SO_4_411214279"}'
    msg = {
        "offset": offset,
        "pageNo": pageNo,
        "limit": "20",
        "csrf_token": "",
        "orderType": "1",
        "cursor": cursor,
        "rid": "R_SO_4_"+str(songId),
        "threadId": "R_SO_4_"+str(songId)
    }
    msg = json.dumps(msg)
    key = '0CoJUm6Qyw8W8jud'
    f = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    e = '010001'
    enctext = AESencrypt(msg, key)
    # 生成长度为16的随机字符串
    i = generate_random_strs(16)

    # 两次AES加密之后得到params的值
    encText = AESencrypt(enctext, i)
    # RSA加密之后得到encSecKey的值
    encSecKey = RSAencrypt(i, e, f)
    return encText, encSecKey


def hotcomments(html, songname, i, pages, total, filepath):

    #过滤表情
    pattern = re.compile(r'[\n\t\r\/]')

    # 写入文件
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write("正在获取歌曲{}的第{}页评论,总共有{}页{}条评论！\n".format(songname, i, pages, total))
    print("正在获取歌曲{}的第{}页评论,总共有{}页{}条评论！\n".format(songname, i, pages, total))

    # 精彩评论
    m = 1
    # 键在字典中则返回True, 否则返回False
    if 'hotComments' in html['data']:
        for item in html['data']['hotComments']:
            # 提取发表热门评论的用户名
            user = item['user']
            # 写入文件
            print("热门评论{}: {} : {}    点赞次数: {}".format(m, user['nickname'], item['content'], item['likedCount']))
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write("热门评论{}: {} : {}   点赞次数: {}\n".format(m, user['nickname'], item['content'], item['likedCount']))
                # 回复评论
                if (item['beReplied'] != None):
                    if len(item['beReplied']) != 0:
                        for reply in item['beReplied']:
                            # 提取发表回复评论的用户名
                            replyuser = reply['user']
                            print("回复：{} : {}".format(replyuser['nickname'], reply['content']))
                            f.write("回复：{} : {}\n".format(replyuser['nickname'], reply['content']))
            m += 1
            # 写入数据库

            userId = user['userId']
            commentId = item['commentId']
            content = pattern.sub('',item['content'])
            likeCount = item['likedCount']
            time = item['time']
            insert_into_mysql(userId, commentId, content, likeCount,time)
            # print(userId, commentId, content, likeCount)
def comments(html, songname, i, pages, total, filepath):

    #过滤表情
    pattern = re.compile(r'[\n\t\r\/]')

    with open(filepath, 'a', encoding='utf-8') as f:
        f.write("\n正在获取歌曲{}的第{}页评论,总共有{}页{}条评论！\n".format(songname, i, pages, total))
    print("\n正在获取歌曲{}的第{}页评论,总共有{}页{}条评论！\n".format(songname, i, pages, total))
    # 全部评论
    j = 1
    i = 0
    for item in html['data']['comments']:
        i += 1
        # 提取发表评论的用户名
        user = item['user']
        print("全部评论{}: {} : {}    点赞次数: {}".format(j, user['nickname'], item['content'], item['likedCount']))
        with open(filepath, 'a', encoding='utf-8') as f:

            f.write("全部评论{}: {} : {}   点赞次数: {}\n".format(j, user['nickname'], item['content'], item['likedCount']))
            # 回复评论
            if (item['beReplied'] != None):
                if len(item['beReplied']) != 0:
                    for reply in item['beReplied']:
                        # 提取发表回复评论的用户名
                        replyuser = reply['user']
                        print("回复：{} : {}".format(replyuser['nickname'], reply['content']))
                        f.write("回复：{} : {}\n".format(replyuser['nickname'], reply['content']))
        j += 1
        # 写入数据库
        userId = user['userId']
        commentId = item['commentId']
        content = pattern.sub('',item['content'])
        likeCount = item['likedCount']
        time = item['time']
        insert_into_mysql(userId, commentId, content, likeCount,time)
        # print(userId, commentId, content, likeCount)
    if (i == 0):
        return 0

def getUserId(html):
    userId = []
    for item in html['data']['comments']:
        user = item['user']
        userId.append(user['userId'])
    return userId

# 插入用户信息
def insert_user_info(html):
    userId = getUserId(html)
    userId = list(set(userId))
    print(userId)
    for item in userId:
        if(UserInfo.is_user_exit(item)==1):
            continue
        else:
            UserInfo.get_user_info(item)
def main():
    # 歌曲id号
    songid = 411214279
    # 歌曲名字
    songname = "雅俗共赏"
    # 文件存储路径
    filepath = songname + ".txt"
    page = 1
    params, encSecKey = get_params(page, songid,-1)

    # 老的api只能爬取到前52页的评论
    # url = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_' + str(songid) + '?csrf_token='
    # 新的api都可以爬 小心被封ip
    url = 'https://music.163.com/weapi/comment/resource/comments/get?csrf_token='
    data = {'params': params, 'encSecKey': encSecKey}

    # 获取第一页评论
    html = get_comments_json(url, data)
    # 评论总数
    total = html['data']['totalCount']
    # 总页数
    pages = math.ceil(total / 20)
    # cursor
    cursor = html['data']['cursor']
    hotcomments(html, songname, page, pages, total, filepath)
    comments(html, songname, page, pages, total, filepath)
    insert_user_info(html)

    # 开始获取歌曲的全部评论
    page = 2
    while page <= 55:
        params, encSecKey = get_params(page, songid,cursor)
        data = {'params': params, 'encSecKey': encSecKey}
        html = get_comments_json(url, data)
        insert_user_info(html)
        cursor = html['data']['cursor']
        # 从第二页开始获取评论
        result = comments(html, songname, page, pages, total, filepath)
        if (result == 0):
            continue
        page += 1


if __name__ == "__main__":
    main()
