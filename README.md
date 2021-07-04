# 网易云评论及用户信息爬取 

## 1.评论信息

网上的教程大部分使用的都是某一个远古API

```
https://music.163.com/weapi/v1/resource/comments/R_SO_4_' + str(songid) + '?csrf_token=
```

但是经过实际爬取之后发现，无法获得52页之后的评论，可能是API接口问题，也可能是网易云的反爬机制。

所以，直接使用Ajax请求中的URL:

```
https://music.163.com/weapi/comment/resource/comments/get?csrf_token=
```

经过core.js的比对，发现这两个请求中的两个参数params和encSecKey的生成方式一样，(具体生成方式请自行百度，网上有太多讲解)但是生成参数时，远古API通过URL中的songid获知歌曲信息，而新的URL通过生成参数时的一个msg参数得到歌曲的id以及当前评论的页面。msg中必须给出页面偏移量offset，每页评论条数limit，当前页面发布评论的最小时间戳cursor(按照毫秒生成)以及当前页码数pageno。具体的构造方式如下：

```python
def get_params(pageNo, songId, cursor):
    # msg也可以写成msg = {"offset":"页面偏移量=(页数-1) *　20", "limit":"20"},offset和limit这两个参数必须有(js)
    # limit最大值为100,当设为100时,获取第二页时,默认前一页是20个评论,也就是说第二页最新评论有80个,有20个是第一页显示的
    # msg = '{"rid":"R_SO_4_1302938992","offset":"0","total":"True","limit":"100","csrf_token":""}'
    # 读js可以知道OFFSET在map不为空的时候是 Math.abs( lastPage - nowPage - 1 )*20
    # cursor是当前页面评论的最小发布时间戳 可以从前一页请求中的cursor获得
    # 偏移量
    if (pageNo == 1):
        offset = 0
    else:
        offset = 40
    # offset和limit以及cursor是必选参数,其他参数是可选的,其他参数不影响data数据的生成
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
```

首页的评论请求的cursor是-1，并且其中会有下一页请求的cursor值，这样就可以逐页的获得所有评论信息。

offset的值是根据js中一个Map来确定的，该Map中存放着每一次请求评论页面的cursor的值。根据
$$
Math.abs( lastPage - nowPage - 1 )*20
$$
可以轻易的得出每次请求的offset的值，如果是逐页请求，则offset就是40......

这两个关键的参数有了之后就可以简单的发请求，将结果转为json后即可获得评论信息。

## 2.用户信息

从1中的评论信息中我们可以得到一个userid，这个userID就是网易云用户的唯一表示。直接向用户信息API发GET请求就可以得到非常详细的用户信息。

```
'https://music.163.com/api/v1/user/detail/' + str(userId)
```

(注意：如果短时间请求数过多可能会被封id，注意使用代理)

