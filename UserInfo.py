import requests
import pymysql
import re

def get_user_json(userId):
    url = 'https://music.163.com/api/v1/user/detail/' + str(userId)
    proxies = {
        "http": "http://127.0.0.1:1080",
        "https": "http://127.0.0.1:1080"
    }
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9',
               'Connection': 'keep-alive',
               'Cookie': 'WM_TID=36fj4OhQ7NdU9DhsEbdKFbVmy9tNk1KM; _iuqxldmzr_=32; _ntes_nnid=26fc3120577a92f179a3743269d8d0d9,1536048184013; _ntes_nuid=26fc3120577a92f179a3743269d8d0d9; __utmc=94650624; __utmz=94650624.1536199016.26.8.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); WM_NI=2Uy%2FbtqzhAuF6WR544z5u96yPa%2BfNHlrtTBCGhkg7oAHeZje7SJiXAoA5YNCbyP6gcJ5NYTs5IAJHQBjiFt561sfsS5Xg%2BvZx1OW9mPzJ49pU7Voono9gXq9H0RpP5HTclE%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eed5cb8085b2ab83ee7b87ac8c87cb60f78da2dac5439b9ca4b1d621f3e900b4b82af0fea7c3b92af28bb7d0e180b3a6a8a2f84ef6899ed6b740baebbbdab57394bfe587cd44b0aebcb5c14985b8a588b6658398abbbe96ff58d868adb4bad9ffbbacd49a2a7a0d7e6698aeb82bad779f7978fabcb5b82b6a7a7f73ff6efbd87f259f788a9ccf552bcef81b8bc6794a686d5bc7c97e99a90ee66ade7a9b9f4338cf09e91d33f8c8cad8dc837e2a3; JSESSIONID-WYYY=G%5CSvabx1X1F0JTg8HK5Z%2BIATVQdgwh77oo%2BDOXuG2CpwvoKPnNTKOGH91AkCHVdm0t6XKQEEnAFP%2BQ35cF49Y%2BAviwQKVN04%2B6ZbeKc2tNOeeC5vfTZ4Cme%2BwZVk7zGkwHJbfjgp1J9Y30o1fMKHOE5rxyhwQw%2B%5CDH6Md%5CpJZAAh2xkZ%3A1536204296617; __utma=94650624.1052021654.1536048185.1536199016.1536203113.27; __utmb=94650624.12.10.1536203113',
               'Host': 'music.163.com',
               'Referer': 'http://music.163.com/',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 '
                             'Safari/537.36',
               }
    try:
        r = requests.get(url,  headers=headers)
        r.encoding = "utf-8"
        if r.status_code == 200:
            # 返回json格式的数据
            return r.json()

    except:
        print("爬取失败!")


def insert_into_mysql(userId, userType, levels, nickname, gender, birthday, description, signature, province, city,
                      listenSongs, vipType, createTime, createDays):
    conn = pymysql.connect(host="192.168.43.202", user="root", password="123456", database="comments", charset="utf8mb4",
                           port=3306)
    cursor = conn.cursor()
    sql = "INSERT INTO user_info(userId,userType,level,nickname,gender,birthday,description,signature,province,city,listenSongs,vipType,createTime,createDays) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    cursor.execute(sql, [userId, userType, levels, nickname, gender, birthday, description, signature, province, city,
                         listenSongs, vipType, createTime, createDays])
    conn.commit()
    cursor.close()
    conn.close()


def get_city_info(city):
    conn = pymysql.connect(host="localhost", user="root", password="184lyj", database="cityno", charset="utf8",
                           port=3306)
    cursor = conn.cursor()

    sql = 'select * from cityno where id= %s;'
    cursor.execute(sql, city)
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result


def is_user_exit(userId):
    conn = pymysql.connect(host="192.168.43.202", user="root", password="123456", database="comments",
                           charset="utf8mb4",
                           port=3306)
    cursor = conn.cursor()

    sql = 'select * from user_info where userId= %s;'
    result = cursor.execute(sql, userId)
    conn.commit()
    cursor.close()
    conn.close()
    return result


def get_user_info(userId):
    html = get_user_json(userId)
    pattern =re.compile(r'[\n\t\r\/]')
    # print(html)
    if(html==None):
        return -1
    else:
        userType = html['profile']['userType']
        level = html['level']
        nickname = pattern.sub('',html['profile']['nickname'])
        gender = html['profile']['gender']
        birthday = html['profile']['birthday']
        description = pattern.sub('',html['profile']['description'])
        signature = pattern.sub('',html['profile']['signature'])
        province = html['profile']['province']
        city = html['profile']['city']
        listenSongs = html['listenSongs']
        vipType = html['profile']['vipType']
        createTime = html['createTime']
        createDays = html['createDays']
        city_info = get_city_info(city)
        if (len(city_info) == 0):
            province = ''
            city = ''
        else:
            province = city_info[0][1]
            city = city_info[0][2]
        insert_into_mysql(userId, userType, level, nickname, gender, birthday, description, signature, province, city,
                          listenSongs, vipType, createTime, createDays)
        return 1


if __name__ == '__main__':
    # userId=1584347191
    # html = get_user_json(userId)
    # # print(html)
    # # print(html['profile']['birthday'])
    # userType = html['profile']['userType']
    # level = html['level']
    # nickname = html['profile']['nickname']
    # gender = html['profile']['gender']
    # birthday = html['profile']['birthday']
    # description = html['profile']['description']
    # signature = html['profile']['signature']
    # province = html['profile']['province']
    # city = html['profile']['city']
    # listenSongs = html['listenSongs']
    # vipType = html['profile']['vipType']
    # createTime = html['createTime']
    # createDays = html['createDays']
    # # data = {
    # #     userId : userId,
    # #     level : html['level'],
    # #     nickname : html['profile']['nickname'],
    # #     gender : html['profile']['gender'],
    # #     birthday : html['profile']['birthday'],
    # #     description : html['profile']['description'],
    # #     signature : html['profile']['signature'],
    # #     province : html['profile']['province'],
    # #     city : html['profile']['city'],
    # #     listenSongs :html['listenSongs'],
    # #     vipType : html['profile']['vipType'],
    # #     createTime :html['createTime'],
    # #     createDays : html['createDays']
    # # }
    # # print(userId,userType,level,nickname,gender,birthday,description,signature,province,city,listenSongs,vipType,createTime,createDays)
    #
    # city_info=get_city_info(city)
    # print(city_info)
    # province = city_info[0][1]
    # city = city_info[0][2]
    # insert_into_mysql(userId,userType,level,nickname,gender,birthday,description,signature,province,city,listenSongs,vipType,createTime,createDays)
    list = [98702178, 3255140547, 1477947081, 541993197, 403913620, 1643576533, 296150069, 1695508058, 135027005,
            294064638]
    # get_user_info(98702178)
    for i in list:
        get_user_info(i)
"level listenSongs userId userType vipType createTime  createDays province city nickname gender birthday description signature"
