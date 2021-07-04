import re
import pymysql


def insert_into_mysql(id, province, city, area):
    conn = pymysql.connect(host="localhost", user="root", password="184lyj", database="cityno", charset="utf8",
                           port=3306)
    cursor = conn.cursor()
    sql = "INSERT INTO cityno(id, province, city, area) VALUES (%s, %s, %s, %s);"
    cursor.execute(sql, [id, province, city, area])
    conn.commit()
    cursor.close()
    conn.close()


with open("城市编号.txt", 'r', encoding='utf8') as wf:
    result = wf.readlines()
    pattern = re.compile(r'[\n\t\r\/]')
    # print(pattern.sub('',result[5]).split(','))
    for item in result:
        data = pattern.sub('', item)
        data = data.replace("中国", '').strip().split(',')
        id = data[0]
        province = data[1]
        if (len(data) <4):
            if(len(data)==2):
                city = ''
                area = ''
            elif(len(data)==3):
                city = data[2]
                area =''
        else:
            city = data[2]
            area = data[3]
        insert_into_mysql(id,province,city,area)
    wf.close()
