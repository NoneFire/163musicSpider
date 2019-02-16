
# encoding:utf-8


import requests
import time
from bs4 import BeautifulSoup
import re
import csv
import json
import pymongo

#下面导入的是本地文件
from PostParamsAES import get_params
from PostParamsAES import get_encSecKey
from ProxyPool import proxy_main_modual  #返回一个经过测试之后能够使用的proxieslist


#设定爬取hotcomments还是comments
MAXPROXIESLIST = 20      #最大代理列表的长度
COMMENTSET = "hotComments"
# 设置header文件
headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
    'referer': 'https://music.163.com/',
    'Host': 'music.163.com',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}
baseurl = 'https://music.163.com'
starturl ='https://music.163.com/discover/artist'
albumclassbaseurl ='https://music.163.com/artist/album?id='
albumbaseurl ='https://music.163.com/album?id='

def parse_starturl(starturl,headers):   #返回的是一个列表
    print("这是parse_starturl，开始从初始页面https://music.163.com/discover/artist开始解析")
    soup0 = BeautifulSoup(requests.get(url=starturl, headers=headers).text, 'lxml')
    baglist = []  #创建一个空的返回列表
    for artistdiv in soup0.find_all(name='ul', class_='nav f-cb'):
        for artistclass in artistdiv.find_all(name='li'):
            artistclasshalfurl = artistclass.a['href']  # 输出各个歌手分类的一半链接
            artistclassname = artistclass.a.string
            print('#解析的第',  '个歌手分类页', artistclassname,artistclasshalfurl)
            if artistclassname == '推荐歌手':
                print('#推荐歌手不进行获取')
                continue  # 跳过本次循环
            if artistclassname == '入驻歌手':
                print('#入驻歌手不进行获取')
                continue  # 跳过本次循环
            bag = [artistclasshalfurl,artistclassname]
            baglist.append(bag)
    print(baglist)
    return baglist   #返回值类似于/discover/artist/cat?id=1001


def parse_artistclasspageurl(artistclasspageurl,headers,proxieslist,proxnum):
    print("这是模块parse_artistclasspageurl，开始解析artistclass的page页面,url为",artistclasspageurl)
    try:
        soup = BeautifulSoup(requests.get(url=artistclasspageurl, headers=headers,proxies=proxieslist[proxnum],timeout=15).text, 'lxml')
        print("当前代理ip", proxieslist[proxnum])
        return soup,proxnum,proxieslist
    except Exception as e:
        proxnum = proxnum+1
        if proxnum >= MAXPROXIESLIST:
            proxieslist=proxy_main_modual()
            proxnum=0
            res = parse_artistclasspageurl(artistclasspageurl, headers, proxieslist, proxnum)
            soup=res[0]
            proxnum=res[1]
            proxieslist=res[2]
            print("当前代理ip", proxieslist[proxnum])
            return soup, proxnum, proxieslist
        else:
            res = parse_artistclasspageurl(artistclasspageurl, headers, proxieslist,proxnum)
            soup = res[0]
            proxnum = res[1]
            proxieslist = res[2]
            print("当前代理ip", proxieslist[proxnum])
            return soup,proxnum,proxieslist


def soup_parse_artistclasspageurl(soup):
    print("soup_parse_artistclasspageurl函数，")
    baglist = []
    s1 = soup.find(name='ul', class_='m-cvrlst m-cvrlst-5 f-cb')
    for artistmessage in s1.find_all(name='li'):  # 找出所有的歌手的li节点信息
        artist = artistmessage.find(name='a', class_='nm nm-icn f-thide s-fc0')
        artistname = artist.string
        artisthref = re.sub('\s', "", artist.attrs['href'])  # 再使用re包替换掉空格
        artistid = re.findall('[0-9]\d*', artisthref)[0]
        artisturl = baseurl + artisthref
        albumclassurl = albumclassbaseurl + str(artistid)
        print("######@@@@@爬取的页面次数", 'artistname', artistname, 'artisturl', artisturl, 'artistid', artistid, 'albumclassurl', albumclassurl)
        bag = [artistname,artistid,artisturl,albumclassurl]
        baglist.append(bag)
    print(baglist)
    return baglist


def parse_albumclassurl(albumclassurl,params,headers,proxieslist,proxnum):  #对这样的链接访问https://music.163.com/artist/album?id=1087200
    print("这是parse_albumclassurl函数,解析url为", albumclassurl)
    try:
        soup = BeautifulSoup(requests.get(url=albumclassurl, headers=headers, params=params,proxies=proxieslist[proxnum],timeout=15).text, 'lxml')
        print("当前代理ip", proxieslist[proxnum])
        return soup, proxnum, proxieslist
    except:
        proxnum = proxnum + 1
        if proxnum >= MAXPROXIESLIST:
            proxieslist = proxy_main_modual()
            proxnum = 0
            res=parse_albumclassurl(albumclassurl, params, headers, proxieslist, proxnum)
            soup = res[0]
            proxnum=res[1]
            proxieslist = res[2]
            print("当前代理ip", proxieslist[proxnum])
            return soup, proxnum, proxieslist
        else:
            res = parse_albumclassurl(albumclassurl, params, headers, proxieslist, proxnum)
            soup = res[0]
            proxnum = res[1]
            proxieslist = res[2]
            print("当前代理ip", proxieslist[proxnum])
            return soup, proxnum, proxieslist


def soup_album_biggestpage(soup): #获取https://music.163.com/#/artist/album?id=10559&limit=12&offset=0页面offset的最大页面数
    try:
        s2 = soup.find(name='div',class_='u-page')
        numlist=[]
        for ss in s2.find_all(name='a'):
            numb=re.findall('\d*',ss.get_text())[0]
            numlist.append(numb)
        biggestpage=(int(max(numlist))-1)*12+1
        print("最大page数量",biggestpage)
        return biggestpage
    except :  # 该异常原因是bs4解析不存在页数对象为AttributeError: 'NoneType' object has no attribute 'find_all',即找不到u-page元素
        biggestpage = 0+1
        print("最大page数量",biggestpage)
        return biggestpage


def soup_parse_albumclassurl(soup):
    print("这是soup_parse_albumclassurl函数")
    baglist = []
    try:
        albumall = soup.find(name='ul', class_='m-cvrlst m-cvrlst-alb4 f-cb')  # 找到所有album的信息的区块
        for album in albumall.find_all(name='li'):
            try:
                albumname = album.div['title']
            except:
                albumname=""
            try:
                albumid = re.findall('[0-9]\d*', album.div.a['href'])[0]
            except:
                albumid=""
            try:
                albumdate = album.find(name='span', class_='s-fc3').string
            except:
                albumdate=""
            albumurl = albumbaseurl + albumid
            bag = [albumname,albumid,albumdate,albumurl]
            baglist.append(bag)
            print("#####@@@@@@", 'albumname', albumname, 'albumid',albumid, 'albumdate', albumdate, 'albumurl', albumurl)
        return baglist
    except:
        return baglist


#解析album的url页面，并以列表的形式返回albumcommentcount,albumsharecount,albumsongcount,songbaglist（歌曲详细信息的列表，包含songid,songname,songurl）
def parse_album_message(albumurl,headers,proxieslist,proxnum):
    print("这是parse_album_message函数",albumurl)
    try:
        soup=BeautifulSoup(requests.get(url=albumurl,headers=headers,proxies=proxieslist[proxnum],timeout=15).text,'lxml')
        return soup, proxnum, proxieslist
    except:
        print(proxnum)
        proxnum = proxnum + 1
        if proxnum >= MAXPROXIESLIST:
            proxieslist = proxy_main_modual()
            proxnum = 0
            res = parse_album_message(albumurl,headers,proxieslist,proxnum)
            soup = res[0]
            proxnum = res[1]
            proxieslist = res[2]
            print("当前代理ip", proxieslist[proxnum])
            return soup, proxnum, proxieslist
        else:
            res = parse_album_message(albumurl, headers, proxieslist, proxnum)
            soup = res[0]
            proxnum = res[1]
            proxieslist = res[2]
            print("当前代理ip", proxieslist[proxnum])
            return soup, proxnum, proxieslist


def soup_parse_album_message(soup):
    baglist = []
    try:
        albumsharecount=re.findall('[0-9]\d*',soup.find(name='a',class_='u-btni u-btni-share ').string)[0]
    except Exception as e:
        print(e)
        albumsharecount = 0
    try:
        albumcommentcount=soup.find(name='span',id='cnt_comment_count').string
    except Exception as e:
        print(e)
        albumcommentcount=0
    try:
        albumsongcount =int(re.findall('[0-9]\d*',(soup.find(name='div',class_='u-title u-title-1 f-cb')).find(name='span',class_='sub s-fc3').string)[0])
    except:
        albumsongcount =0
    try:
        albumdiscom=re.sub('发行公司：\n',"",(soup.find(name='div',class_='topblk').find(text=re.compile("发行公司"))).parent.parent.get_text()) #获取专辑的发行公司
    except:
        albumdiscom = ""
    #解析album中的歌曲信息，并以列表的形式输出
    try:
        s4=soup.find(name='ul', class_='f-hide')
        for songmessage in s4.find_all(name='li'):
            songall = songmessage.find(name='a')
            songhref=re.sub('\s',"",songall['href'])
            songname=songall.string
            songurl = 'https://music.163.com' + songhref
            songid = re.findall('[0-9]\d*',songhref)[0]
            bag = [songid,songname,songurl]  #创建列表存储歌曲id，name，url
            baglist.append(bag) #专辑内歌曲作为list传出
    except:
        bag = ["","",""]
        baglist.append(bag)
    return albumsharecount,albumcommentcount,albumsongcount,baglist,albumdiscom


#解析song的url页面，好像没有什么需要解析的啊？？？？解析歌手id，可能会有重复的歌曲有两个id，之后进行songid去重，
def parse_song_message(songurl,headers,proxieslist,proxnum):
    print("解析song的url页面",songurl)
    try:
        soup=BeautifulSoup(requests.get(url=songurl,headers=headers,proxies=proxieslist[proxnum],timeout=15).text,'lxml')
        print("当前代理ip", proxieslist[proxnum])
        return soup, proxnum, proxieslist
    except:
        proxnum = proxnum + 1
        if proxnum >= MAXPROXIESLIST:
            proxieslist = proxy_main_modual()
            proxnum = 0
            res = parse_album_message(songurl, headers, proxieslist, proxnum)
            soup = res[0]
            proxnum = res[1]
            proxieslist = res[2]
            print("当前代理ip", proxieslist[proxnum])
            return soup, proxnum, proxieslist
        else:
            res = parse_album_message(songurl, headers, proxieslist, proxnum)
            soup = res[0]
            proxnum = res[1]
            proxieslist = res[2]
            print("当前代理ip", proxieslist[proxnum])
            return soup, proxnum, proxieslist


def soup_parse_song_message(soup):
    s5 = soup.find(name='div',class_='tit')
    try:
        truesongname = s5.find(name='em',class_='f-ff2').string
    except:
        truesongname =""
    try:
        songnamesubtit = s5.find(name='div',class_='subtit f-fs1 f-ff2').string
    except:
        songnamesubtit = ""

    ss5=soup.find(name='p',class_='des s-fc4')
    try:
        songsartist1 = ss5.find_all(name='a',class_='s-fc7')[0].string
    except:
        songsartist1=""
    try:
        songsartist2 = ss5.find_all(name='a',class_='s-fc7')[1].string
    except:
        songsartist2 = ""
    print(truesongname,songnamesubtit,songsartist1,songsartist2)
    return truesongname,songnamesubtit,songsartist1,songsartist2


def parse_get_songcomment(songurl,songid,proxieslist,proxnum,page):       #获取歌曲评论数量并返回这个值
    print("parse_get_songcommentcount函数")
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
        'referer': songurl,
        'Host': 'music.163.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }
    commentrequesturl = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_' + str(songid) + '?csrf_token='
    if page ==0:
        params = get_params(0)
    else :
        params = get_params(page)

    encSeckey = get_encSecKey()
    data = {
        'params': params,
        'encSecKey': encSeckey
    }
    try:
        jsoncontent = json.loads(str(requests.post(url=commentrequesturl, headers=headers, data=data, proxies=proxieslist[proxnum],timeout=15).content.decode('utf-8')))
        print("当前代理ip",proxieslist[proxnum])
        return jsoncontent, proxnum, proxieslist
    except:
        proxnum = proxnum + 1
        if proxnum >= MAXPROXIESLIST:
            proxieslist = proxy_main_modual()
            proxnum = 0
            res = parse_get_songcomment(songurl,songid,proxieslist,proxnum,page)
            jsoncontent = res[0]
            proxnum = res[1]
            proxieslist = res[2]
            print("当前代理ip", proxieslist[proxnum])
            return jsoncontent, proxnum, proxieslist
        else:
            res = parse_get_songcomment(songurl,songid,proxieslist,proxnum,page)
            jsoncontent = res[0]
            proxnum = res[1]
            proxieslist = res[2]
            print("当前代理ip", proxieslist[proxnum])
            return jsoncontent, proxnum, proxieslist

def soup_get_songcommentcount(jsoncontent):
    try:
        songcommentcount=jsoncontent["total"]
    except :
        songcommentcount =0
    return int(songcommentcount)  #转换为数字


#创建存储函数，并判定存储的内容，如果为1存储头名称
def store_comments_dict(resultdictdata,i):   #i用来判定存储的内容是什么
    print("这是存储函数")
    if i==0:
        with open("storedictdata.csv", 'a', encoding='utf-8-sig', newline='') as csvfile:
            fieldname = ['artistclassname','artistname','artistid','artisturl','albumname','albumid','albumurl','albumdate','albumdiscom','albumcommentcount','albumsharecount','albumsongcount','songname','songid','songurl','truesongname','songnamesubtit','songsartist1','songsartist2','commentscount','commentId','userID','username','userpicurl','userviptype','likedcount','commenttime','commentcontent','beReplieduserID','beRepliedusername','beRepliedcommentId','beRepliedcommentcontent']
            writecsv = csv.DictWriter(csvfile, fieldnames=fieldname)
            writecsv.writeheader()
    else:
        with open("storedictdata.csv",'a',encoding='utf-8-sig',newline ='') as csvfile:
            fieldname = ['artistclassname','artistname','artistid','artisturl','albumname','albumid','albumurl','albumdate','albumdiscom','albumcommentcount','albumsharecount','albumsongcount','songname','songid','songurl','truesongname','songnamesubtit','songsartist1','songsartist2','commentId','commentscount','userID','username','userpicurl','userviptype','likedcount','commenttime','commentcontent','beReplieduserID','beRepliedusername','beRepliedcommentId','beRepliedcommentcontent']
            writecsv = csv.DictWriter(csvfile,fieldnames=fieldname)
            writecsv.writerow(resultdictdata)


def soupandstore_songcomment(jsontext,songdictdata,n):
    jsondict = jsontext
    m = 0 #判定存储的是什么内容
    for comments in jsondict[COMMENTSET]:  # 爬取hotcomment
        try:
            userID = (comments['user'])['userId']
            username = (comments['user'])['nickname']
            userviptype = (comments['user'])['vipType']
            userpicurl = (comments['user'])['avatarUrl']
            likedcount = comments['likedCount']
            commentId = comments['commentId']
            commenttime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(comments['time'] / 1000)))
            commentcontent = comments['content']
            if comments['beReplied']:
                beReplied = comments['beReplied'][0]  # 遍历beReplied这个list,不用遍历，只有1个回复，提取对应字典信息
                beReplieduserID = (beReplied['user'])['userId']
                beRepliedusername = (beReplied['user'])['nickname']
                beRepliedcommentId = beReplied['beRepliedCommentId']
                beRepliedcommentcontent = beReplied['content']
            else:
                beReplieduserID = ""
                beRepliedusername = ""
                beRepliedcommentId = ""
                beRepliedcommentcontent = ""
            commentsdictdata = {
                'commentId': commentId,
                'userID': userID,
                'username': username,
                'userpicurl': userpicurl,
                'userviptype': userviptype,
                'likedcount': likedcount,
                'commenttime': commenttime,
                'commentcontent': commentcontent,
                'beReplieduserID': beReplieduserID,
                'beRepliedusername': beRepliedusername,
                'beRepliedcommentId': beRepliedcommentId,
                'beRepliedcommentcontent': beRepliedcommentcontent
            }
            resultdictdata = dict(songdictdata, **commentsdictdata)  # 字典合并
            store_comments_dict(resultdictdata, i=n+m)
            m = m + 1
        except Exception as e:
            print("soupandstore_songcomment模块出现问题，问题为",e)
            print("设定本条内容为空")
            commentsdictdata = {}
            resultdictdata = dict(songdictdata, **commentsdictdata)  # 字典合并
            store_comments_dict(resultdictdata, i=n+m)
            m=m+1




def parse_song_lyric():#解析歌词，暂定函数，由于未解析加密参数，先不运行
    print('ss')

def store_mongpDB():#调用数据库存储
    client = pymongo.MongoClient(host='localhost',port=27017)
    db = client.test #指定test数据库
    collection = db.students  #指定db.students集合
    student={
        'id':'123',
        'name':'jordan',
        'age':'20',
        'gender':'male'
    }
    result = collection.insert_one(student)
    print(result.inserted_id)
    print(result)
    print(type(result))
    print(collection.find_one({'name':'jordan'}))

def crawled_artistid():#断点判定,从csv文件里读取有效id数据，进行判定
    with open('crawledartistid.csv','r+') as csvfile:
        csvreader = csv.reader(csvfile)
        finallist = list(csvreader)
    return finallist

#函数的起点,加入断点续传功能，传入参数artistid
def main(breakpointlist):

    print('开始解析starturl，从https://music.163.com/discover/artist这个链接开始，获取歌手分类，并进一步爬取歌手名字')

    proxieslist = proxy_main_modual()  # 设定代理ip，直到无法获取信息再切换ip，
    proxnum = 0
    n = 0  # 这是爬取的计数方式
    artistclasslist = parse_starturl(starturl, headers)  # 传入基础baseurl和headers，解析出artistclasshalfurl以及artistclassname


    for a in artistclasslist:  #对返回的列表artistclasslist进行遍历操作并赋值循环
        artistclasshalfurl = a[0]
        artistclassname = a[1]
        print("开始解析歌手分类页面")
        for pagenum in range(0,91):  #开始解析歌手分类页面的连接页面,页面从0,65到90页，这个网址https://music.163.com/discover/artist/cat?id=1001&initial=65
            if 0<pagenum<65:
                continue
            else :
                pagenum = str(pagenum)
                artistclasspageurl = baseurl + artistclasshalfurl + '&initial=' + pagenum  # 构造artistclass各个page的url
                print("当前解析歌手分类页面",artistclassname)
                res = parse_artistclasspageurl(artistclasspageurl,headers,proxieslist,proxnum)
                soup = res[0]
                proxnum = res[1]
                proxieslist = res[2]
                artistalbumlist = soup_parse_artistclasspageurl(soup)

                for b in artistalbumlist: #对返回的列表artistalbumlist进行遍历操作url
                    artistname=b[0]
                    artistid=b[1]
                    artisturl=b[2]
                    albumclassurl=b[3] #这是歌手主界面的album页面地址，类似https://music.163.com/artist/album?id=1087200
                    #插入断点续传功能

                    if [artistid] not in breakpointlist:#不等于就继续，等于continue,跳过
                        print("not in，继续操作")
                        param={'limit': '12', 'offset':0}
                        result = parse_albumclassurl(albumclassurl,param, headers, proxieslist, proxnum)
                        soupres = result[0]
                        proxnum = result[1]
                        proxieslist = result[2]
                        biggestpage = soup_album_biggestpage(soupres)
                        for Q in range(0,biggestpage,12): #对album的页数进行遍历操作
                            params= {'limit': '12', 'offset':Q}      #这是设置访问歌手专辑page需要get的参数
                            res1 = parse_albumclassurl(albumclassurl,params,headers,proxieslist,proxnum)
                            soup1=res1[0]
                            proxnum = res1[1]
                            proxieslist =res1[2]
                            albumlist = soup_parse_albumclassurl(soup1)
                            for c in albumlist:
                                albumname=c[0]
                                albumid=c[1]
                                albumdate=c[2]
                                albumurl=c[3]
                                res2 =  parse_album_message(albumurl,headers,proxieslist,proxnum) #开始解析album message
                                soup2 = res2[0]
                                proxnum = res2[1]
                                proxieslist = res2[2]
                                albumallmessage = soup_parse_album_message(soup2)
                                albumcommentcount = albumallmessage[0]
                                albumsharecount = albumallmessage[1]
                                albumsongcount = albumallmessage[2]
                                songlist = albumallmessage[3]
                                albumdiscom = albumallmessage[4]
                                for d in songlist:
                                    n=n+1
                                    songid = d[0]
                                    songname = d[1]
                                    songurl = d[2]
                                    res3 =parse_song_message(songurl,headers,proxieslist,proxnum)  #调用爬取歌曲信息的函数
                                    soup3 =res3[0]
                                    proxnum = res3[1]
                                    proxieslist = res3[2]
                                    songallmessage = soup_parse_song_message(soup3)
                                    truesongname=songallmessage[0]
                                    songnamesubtit=songallmessage[1]
                                    songsartist1=songallmessage[2]
                                    songsartist2=songallmessage[3]
                                    if COMMENTSET == "hotComments":  #爬取hotComments
                                        print("当前进行",COMMENTSET,"的爬取")
                                        page = 0  #这个page指的是传给getparams（）的参数，为0
                                        songcommentcount=20
                                        songdictdata = {  # 将所有数据打包为一个字典文件传输到解析评论得页面中并输出存储
                                            'artistclassname': artistclassname,
                                            'artistname': artistname,
                                            'artistid': artistid,
                                            'artisturl': artisturl,
                                            'albumname': albumname,
                                            'albumid': albumid,
                                            'albumurl': albumurl,
                                            'albumdate': albumdate,
                                            'albumdiscom': albumdiscom,
                                            'albumcommentcount': albumcommentcount,
                                            'albumsharecount': albumsharecount,
                                            'albumsongcount': albumsongcount,
                                            'songname': songname,
                                            'songid': songid,
                                            'songurl': songurl,
                                            'truesongname': truesongname,
                                            'songnamesubtit': songnamesubtit,
                                            'songsartist1': songsartist1,
                                            'songsartist2': songsartist2,
                                            'commentscount': songcommentcount
                                        }
                                        print("@@@@@@ @@@@@@@@@@@@@@")
                                        print("歌曲解析url", songurl, "解析歌曲的次数为", n)
                                        jsonres1 = parse_get_songcomment(songurl, songid, proxieslist, proxnum, page)
                                        jsontext = jsonres1[0]
                                        proxnum = jsonres1[1]
                                        proxieslist = jsonres1[2]
                                        print("开始进行评论json的解析存储")
                                        print("                       SSSSSSSSSSSSSSS")
                                        soupandstore_songcomment(jsontext, songdictdata,n)
                                        print("执行下一个歌曲循环@##################################")
                                        print('')
                                        print('')
                                        print('')
                                    elif COMMENTSET == "comments":
                                        jsonres = parse_get_songcomment(songurl, songid, proxieslist, proxnum,page=0)  # 获取歌曲评论总数
                                        jsoncontent=jsonres[0]
                                        proxnum=jsonres[1]
                                        proxieslist=jsonres[2]
                                        songcommentcount = soup_get_songcommentcount(jsoncontent)
                                        if songcommentcount % 20 == 0:
                                            if int(songcommentcount / 20) > 0: #如果时0条评论的呢？返回1
                                                page=int(songcommentcount / 20)
                                            else:
                                                page=1
                                        else:
                                            page = int(songcommentcount // 20 + 1)  # //向下取整
                                        print("@@@@@@ @@@@@@@@@@@@@@")
                                        print("当前开始歌曲评论，歌曲解析url",songurl,"解析歌曲的次数为",n,"解析歌曲评论的内容",COMMENTSET)
                                        print("@@@@@@ @@@@@@@@@@@@@@")
                                        songdictdata = {  # 将所有数据打包为一个字典文件传输到解析评论得页面中并输出存储
                                                               'artistclassname': artistclassname,
                                                               'artistname': artistname,
                                                               'artistid': artistid,
                                                               'artisturl': artisturl,
                                                               'albumname': albumname,
                                                               'albumid': albumid,
                                                               'albumurl': albumurl,
                                                               'albumdate': albumdate,
                                                               'albumdiscom': albumdiscom,
                                                               'albumcommentcount': albumcommentcount,
                                                               'albumsharecount': albumsharecount,
                                                               'albumsongcount': albumsongcount,
                                                               'songname': songname,
                                                               'songid': songid,
                                                               'songurl': songurl,
                                                               'truesongname': truesongname,
                                                               'songnamesubtit': songnamesubtit,
                                                               'songsartist1': songsartist1,
                                                               'songsartist2': songsartist2,
                                                               'commentscount': songcommentcount
                                            }
                                        for f in range(0, page):  #传入上面判定的page
                                            jsonres1 = parse_get_songcomment(songurl, songid, proxieslist, proxnum,page)
                                            jsontext = jsonres1[0]
                                            print(jsontext)
                                            proxnum = jsonres1[1]
                                            proxieslist = jsonres1[2]
                                            soupandstore_songcomment(jsontext,songdictdata,n)
                                            print("执行下一个歌曲循环@##################################")
                                            print('')
                                            print('')
                                            print('')

                                    else:
                                        page = int(input("COMMENTSET设定错误，只允许设定为hotcomments或者comments,请终止"))
                    else:
                        print("这是断点续传，跳过")
                        continue



#主函数@@@@@@@@@@@@@@@@
if __name__ == '__main__':
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print('@@@@@@@@@@@@@@@@@@@                                              @@@@@@@@@@@@@@@@@@@@')
    print('@@@@@@@@@@@@@@@@@@@              开始爬取网易云音乐                @@@@@@@@@@@@@@@@@@@@')
    print('@@@@@@@@@@@@@@@@@@@              这是起点                         @@@@@@@@@@@@@@@@@@@@')
    print('@@@@@@@@@@@@@@@@@@@              by WiteAndBlock                 @@@@@@@@@@@@@@@@@@@@')
    print('@@@@@@@@@@@@@@@@@@@              立下的flag完成了                 @@@@@@@@@@@@@@@@@@@@')
    print('@@@@@@@@@@@@@@@@@@@                                              @@@@@@@@@@@@@@@@@@@@')
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

    breakpointlist = crawled_artistid()
    main(breakpointlist)



    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print('@@@@@@@@@@@@@@@@@@@                                              @@@@@@@@@@@@@@@@@@@@')
    print('@@@@@@@@@@@@@@@@@@@              解析完成，恭喜恭喜                @@@@@@@@@@@@@@@@@@@@')
    print('@@@@@@@@@@@@@@@@@@@              这是终点                         @@@@@@@@@@@@@@@@@@@@')
    print('@@@@@@@@@@@@@@@@@@@                                              @@@@@@@@@@@@@@@@@@@@')
    print('@@@@@@@@@@@@@@@@@@@              立下的flag完成了                 @@@@@@@@@@@@@@@@@@@@')
    print('@@@@@@@@@@@@@@@@@@@                                              @@@@@@@@@@@@@@@@@@@@')
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')



