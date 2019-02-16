# encoding:utf-8


import requests
from bs4 import BeautifulSoup
import json

#这是相关的常量，即为相关的配置文件
KEYSET="api"
IPTESTURL = "https://music.163.com"
IPTESTHEAD = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
    'referer': 'https://music.163.com/',
    'Host': 'music.163.com',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}


def proxy_get_modual(key):#开始调用代理池爬取，设定两个爬取方案，传入参数key = "api",使用api操作，传入参数key = "free",从网上爬取proxy
    if key == "api":
        apiurl ='http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=1e9c662ded0f4e3dab05b55ced6c8e8a&orderno=YZ20192120709aULiGT&returnType=2&count=20'
        print("通过api方式获取代理ip")
        try:
            jsontext = requests.get(url=apiurl,timeout=10).text
        except Exception as e:
            print("get失败或者超时",e)
            try:
                jsontext = requests.get(url=apiurl, timeout=10).text
            except Exception as e:
                print("2遍了，真的get不到了，再试一次，再出错结束执行，重新改变api吧",e)
                jsontext = requests.get(url=apiurl, timeout=10).text
        print(jsontext) #没有异常，
        jsondict=json.loads(jsontext)#转换为dict
        ippoollist=[]
        if jsondict['ERRORCODE']=='0':
            for ippro in jsondict['RESULT']:
                ipproxy=str(ippro['ip'])+':'+str(ippro['port'])
                ippoollist.append(ipproxy)
        else:
            print(jsondict['ERRORCODE'],'获取ip错误，请检查链接api')
            input("等待给api续费")
            ippoollist = proxy_get_modual("api")  #获取失败就重新获取
        print(ippoollist)
        return ippoollist
    elif key == "free":
        print("爬取西次免费代理，开始操作...")
        headers = {
            'Accept - Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Host': 'www.xicidaili.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'cookie': '_free_proxy_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJTUxZjYyNWI0OGRiZWMyYzBmNzlkZTJjZGVlM2MxZGM3BjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMXpvb3pPNmVXd3l6aEFhWVFRYXQ0Zk5MK0JKTWp2OUtkMitpaXQrdVZ6K3M9BjsARg%3D%3D--48666165f0e8e24873b868a59212cc3a80c240f9; Hm_lvt_0cf76c77469e965d2957f0553e6ecf59=1549893751; Hm_lpvt_0cf76c77469e965d2957f0553e6ecf59=1549893768'
        }
        freeurl = 'https://www.xicidaili.com/nn/1'
        soup = BeautifulSoup(requests.get(url=freeurl, headers=headers).text, 'lxml')
        s = soup.find(name='table', id='ip_list')
        ippoollist = []
        for ss6 in s.find_all(name='tr'):
            sss6 = ss6.find_all(name='td')
            if sss6:
                ipaddress = sss6[1].string
                ipport = sss6[2].string
                ipproxy = str(ipaddress) + ':' + str(ipport)
                ippoollist.append(ipproxy)
            else:
                continue
        print(ippoollist)
        return ippoollist
    elif key=="ip":
        ippoollist=['171.13.36.167:47208', '117.57.90.48:36346', '123.53.133.150:26843', '27.157.74.91:39126', '180.104.76.165:43020', '123.54.249.50:36224', '223.151.64.80:38223', '183.146.157.147:32828', '123.54.225.23:47831', '123.161.154.74:43716', '27.156.214.122:42603', '114.224.86.18:28292', '114.228.200.61:29710', '115.221.121.209:22781', '140.224.156.230:42260', '115.226.154.7:28267', '120.43.59.126:44144', '115.226.148.107:42799', '106.46.4.156:38080', '59.61.39.79:40728']
        return ippoollist
    else :
        key = input("传递参数错误，继续请输入key内容（api或者free）")
        ippoollist = proxy_get_modual(key)
        print(ippoollist)
        return ippoollist


def proxy_test_modual(ippoollist,iptesturl,iptestheader):  #将获取到得ip代理池子进行测试，并传入第二个参数，获取测试链接
    proxieslist=[]  #可用proxies
    for ippool in ippoollist:
        proxies = {
                'http':'http://'+ ippool,
                'https': 'https://' + ippool
            }
        try:
            print('测试响应情况')
            print(requests.get(url=iptesturl,proxies=proxies,headers=iptestheader,timeout=4).status_code) #测试响应情况
            proxieslist.append(proxies)
        except Exception as e:
            print("下一个",e)
            continue
    print("最终可用代理为")
    print(proxieslist)
    return proxieslist  #返回可用代理列表


def proxy_main_modual():
    #key = input("请输入代理ip获取方式，api或者free")
    ippoollist = proxy_get_modual(KEYSET)  # get到ip代理得链接，存入proxieslist列表中
    proxieslist = proxy_test_modual(ippoollist=ippoollist, iptesturl=IPTESTURL, iptestheader=IPTESTHEAD)  # 对获取得ip地址进行测试并返回可用proxieslist列表
    return proxieslist          #return  proxieslist这个参数


if __name__ == '__main__':
    proxy_main_modual()