#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
import smtplib
import random
import datetime
import time
import os
import re
import requests
from email.mime.text import MIMEText

PT_Sites = (    #  pt站信息，没加注释的字段最好不要改
    {
        'address': 'https://tvhome.club/',  #  pt站完整地址，注意格式，最后必须带/
        'encoding': 'utf-8',                #  除非整页汉字乱码，否则不要修改
        'torrents': 'torrents.php',         #  种子页面地址，php后可以跟搜索条件，参见gztown
        'attendance': 'attendance.php',     #  签到地址
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',     #  cookie，用chrome摘，用于免输用户名密码登录
            'Cookie': '',
            'Host': 'tvhome.club',          #  必须改成跟上面的pt站完整地址一致，否则打不开网页
            'Referer': 'https://tvhome.club/torrents.php',  #  这个字段没有也行，避免被网站ban
            'Upgrade-Insecure-Requests': '1',  #  user-agent懂的可以改，模拟不同的浏览器
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/65.0.3325.181 Chrome/65.0.3325.181 Safari/537.36'
        },
        'welcomeback': '欢迎回来',  #  跟下两个字段一起用于校验是否成功打开了种子页面
        'nsigned': '签到得魔力',    #  页面匹配到此字段说明可以去签到
        'signed': '签到已得',       #  页面匹配到此字段说明今天已经签到过了
        'torrentstablekey': ' class="torrents"',  #  提取种子页面种子表的关键字，程序中跟<table配合使用
        'torrentpublishtime': 120,  #  筛选条件-发布时间，单位分钟，小于此值会被选中
        'torrentsize': 40           #  筛选条件-种子大小，单位GB，大于此值会被选中
    },                          #  后面的注释懒得一个一个加了，跟这个一样，自己看吧
    {
        'address': 'https://pt.gztown.net/',
        'encoding': 'utf-8',
        'torrents': 'torrents.php?incldead=1&spstate=2&inclbookmarked=0&search=&search_area=0&search_mode=0',
        'attendance': 'attendance.php',
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': '',
            'Host': 'pt.gztown.net',
            'Referer': 'https://pt.gztown.net/torrents.php',
            'Upgrade-Insecure-Requests': 'i1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/65.0.3325.181 Chrome/65.0.3325.181 Safari/537.36'
        },
        'welcomeback': '欢迎回来',
        'nsigned': '签到得魔力',
        'signed': '签到已得',
        'torrentsize': 40,
        'torrentpublishtime': 120,
        'torrentstablekey': ' class="torrents"'
    },
    {
        'address': 'https://hdhome.org/',
        'encoding': 'utf-8',
        'torrents': 'torrents.php?standard1=1&standard2=1&incldead=1&spstate=2&inclbookmarked=0&search=&search_area=0&search_mode=0',
        'attendance': 'attendance.php',
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': '',
            'Host': 'hdhome.org',
            'Referer': 'https://hdhome.org/torrents.php',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/65.0.3325.181 Chrome/65.0.3325.181 Safari/537.36'
        },
        'welcomeback': '欢迎回来',
        'nsigned': '签到得魔力',
        'signed': '签到已得',
        'torrentsize': 40,
        'torrentpublishtime': 120,
        'torrentstablekey': ' class="torrents"'
    },
    {
        'address': 'https://ourbits.club/',
        'encoding': 'utf-8',
        'torrents': 'torrents.php?standard1=1&standard5=1&incldead=1&spstate=2&inclbookmarked=0&search=&search_area=0&search_mode=0',
        'attendance': 'attendance.php',
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': '',
            'Host': 'ourbits.club',
            'Referer': 'https://ourbits.club/torrents.php',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/65.0.3325.181 Chrome/65.0.3325.181 Safari/537.36'
        },
        'welcomeback': '欢迎回来',
        'nsigned': '签到得魔力',
        'signed': '签到已得',
        'torrentsize': 40,
        'torrentpublishtime': 120,
        'torrentstablekey': ' class="torrents"'
    },
)

def GetTimeStamp():
    return( str( datetime.date.today() ) + ' ' + time.strftime('%H:%M:%S') )

def WriteLog( b, s ):
    if ( b == 0 ):  #  找到种子就写入log文件，否则输出到屏幕，避免log文件过大降低性能
        f = open( log_filename, 'a', encoding='utf-8' )
        f.write( GetTimeStamp() + ' ' + s + '\n' )
        f.close()
    else:
        print( GetTimeStamp() + ' ' + s )

def SleepaWhile():
    time.sleep( random.uniform( 2, 6 ) )

def GetHTML( url, headers, encoding ):
    SleepaWhile()
    try:
        requests.packages.urllib3.disable_warnings()  #  关https警告
        r = requests.get( url, headers=headers, verify=False )
        r.encoding = encoding
        return( r.text )
    except:
        WriteLog( 0, url + ' couldn\'t open.' )
        return( '' )

def ExtractDownloadHref( html ):  #  提取种子的超链接
    m = re.search( r'<a.+href=[\'"](download\.php[^\'"]+)[\'"]', html )
    if ( m == None ):
        return( '' )
    else:
        return( m.group(1) )

def StripHTML( name, s1, s2, html ):  #  同下面那个函数，区别是剥除标签中所有内容
    l = len( html )
    ls1 = len( s1 )
    ls2 = len( s2 )
    p1 = html.find( s1 + name )  #  p1指向标签开始位置
    if ( p1 < 0 ):
        return ''
    c = 1  #  嵌套计数器
    p2 = p1 + ls1 + len(name)  #  初始化p2位置，在下面循环里往后移动p2
    while ( c > 0 ):  #  配对成功计数器归0结束循环
        p3 = html[p2:].find( s1 )
        p4 = html[p2:].find( s2 )
        if ( p3 < 0 ):
            p3 = l
        if ( p4 < 0 ):
            p4 = l
        if ( p3 < p4 ):
            p2 = p2 + p3 + ls1
            c += 1  #  找到一层嵌套，计数器加一
        elif ( p4 < p3 ):
            p2 = p2 + p4 + ls2
            c -= 1  #  结束一层嵌套，计数器减一
        else:
            return( html[:p1] )  #  配对失败，头标签比尾标签多，垃圾网页，返回头标签之前的所有内容
    return( html[:p1] + html[p2:] )  #  循环结束配对成功 oh yeah!

def ExtractHTML( name, s1, s2, html ):  #  配对s1+name|s2标签，提取该标签中所有内容，可处理嵌套结构
    l = len( html )
    ls1 = len( s1 )
    ls2 = len( s2 )
    p1 = html.find( s1 + name )
    if ( p1 < 0 ):
        return( '' )
    c = 1
    p2 = p1 + ls1 + len(name)
    while ( c > 0 ):
        p3 = html[p2:].find( s1 )
        p4 = html[p2:].find( s2 )
        if ( p3 < 0 ):
            p3 = l
        if ( p4 < 0 ):
            p4 = l
        if ( p3 < p4 ):
            p2 = p2 + p3 + ls1
            c += 1
        elif ( p4 < p3 ):
            p2 = p2 + p4 + ls2
            c -= 1
        else:
            return( html[p1:] )
    return( html[p1:p2] )

def StripallTags( html ):  #  剥除所有标签，同下面的美化网页
    html = re.sub( '//<!\[CDATA\[[^>]*//\]\]>', '', html )
    html = re.sub( '<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', '', html )
    html = re.sub( '<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', '', html )
    html = re.sub( '</?\w+[^>]*>', '', html )
    html = re.sub( '<!--[^>]*-->', '', html )
    html = re.sub( '[\f\r\t\v]+', '', html )
    html = re.sub( '&nbsp', ' ', html )
    html = re.sub( '<br\s*?/?>', '\n', html )
    html = re.sub( '[\n ]+\n+', '\n', html )
    html = re.sub( r'<[^>]*>', '', html )
    return( html )

def PrretifyHTML( html ):  #  美化网页, md群晖装不上美丽汤这个函数只好自己写
    html = re.sub( '<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', '', html )
    html = re.sub( '<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', '', html )
    html = re.sub( r'valign="[^"]*"', '', html )
    html = re.sub( r'align="[^"]*"', '', html )
    html = re.sub( r'width="[^"]*"', '', html )
    html = re.sub( r'style="[^"]*"', '', html )
    html = re.sub( r"valign='[^']*'", '', html )
    html = re.sub( r"align='[^']*'", '', html )
    html = re.sub( r"width='[^']*'", '', html )
    html = re.sub( r"style='[^']*'", '', html )
    return( html )

#  程序起点
mail_content = ''
log_filename = re.sub( r'/[^/]+$', '', os.path.abspath(__file__) ) + '/pt.log'
try:                        #  这个日志文件过大或者出现问题，可以直接删除，不影响程序运行
    f = open( log_filename, 'r', encoding='utf-8' )
    log_content = f.read()  #  读入日志文件，其中保存有以前筛选出的种子信息，避免晒出重复种子
    f.close()
except:
    log_content = ''
time.sleep( random.uniform( 1, 120 ) )  #  随机休眠避免网站识别
for pt_site in PT_Sites:                #  根据上面的数据结构循环遍历各pt站
    url = pt_site['address'] + pt_site['torrents']
    headers = pt_site['headers']
    encoding = pt_site['encoding']
    html = GetHTML( url, headers, encoding )  #  读取种子页面
    content = StripallTags( html )            #  剥除所有标签，便于比对，不剥也没事
    b = ( content.find( pt_site['signed'] ) >= 0 )  #  三个条件的逻辑判断，用位移运算吧，虽然看着累但我写着简单
    b = ( b << 1 ) | ( content.find( pt_site['nsigned'] ) >= 0 )
    b = ( b << 1 ) | ( content.find( pt_site['welcomeback'] ) >= 0 )
    if ( ( b != 3 ) and ( b != 5 ) ):   #  处理非正常页面
        WriteLog( 1, url + ' wrong page, dump html data below, check the url and the cookies plz' )
        WriteLog( 1, content )          #  此函数第一个参数的用法:0写入日志文件，1不写文件只输出到屏幕
        WriteLog( 1, str(headers) )
        continue
    if ( b == 3 ):  #  需要签到
        url = pt_site['address'] + pt_site['attendance']
        headers = pt_site['headers']
        encoding = pt_site['encoding']
        html = GetHTML( url, headers, encoding )  #  读取签到页面
        content = StripallTags( html )
        matcher = re.search( pt_site['signed']+'\d*', content )
        if ( matcher != None ):  #  签到成功
            WriteLog( 0, pt_site['address'] + ' ' + matcher.group( 0 ) + '魔力' )  #  这个要写文件
            url = pt_site['address'] + pt_site['torrents']
            headers = pt_site['headers']
            encoding = pt_site['encoding']
            html = GetHTML( url, headers, encoding )  #  重新读取种子页面
        else:
            WriteLog( 1, url + ' something might be wrong, \'ll sign next round' )
            WriteLog( 1, content )
            continue
    content = ''  #  找到的种子存在这里，这个变量前面用过，懒得起名字了，这里重新用一下不影响
    torrents = ExtractHTML( pt_site['torrentstablekey'], '<table', '/table>', html )  #  提取种子表
    for i in range(100):  #  前100个种子，本来这个循环50就够，谁知道ourbits置顶那么多...
        torrent = ExtractHTML( r'', r'<tr', r'/tr>', torrents )  #  种子表里提取1行
        torrents = StripHTML( r'', r'<tr', r'/tr>', torrents )
        tc = ['' for j in range(8)]
        for j in range(8):
            tc[j] = ExtractHTML( r'', r'<td', r'/td>', torrent )  #  1行里提取8列
            torrent = StripHTML( r'', r'<td', r'/td>', torrent )
        torrenturl = pt_site['address'] + ExtractDownloadHref( tc[1] )
        torrentname = ExtractHTML( r'', r'<a ', r'/a>', tc[1] )  #  提取种子下载地址及名称
        torrentname = StripallTags( torrentname )
        tc[3] = StripallTags( tc[3] )
        tc[4] = StripallTags( tc[4] )
        tc[5] = StripallTags( tc[5] )  #  从第5列开始分别是上传数量下载数量完成数量
        tc[6] = StripallTags( tc[6] )
        tc[7] = StripallTags( tc[7] )
        r = re.search( r'^(\d+)时(\d+)分', tc[3] )  #  解析发种时间
        if ( r != None ):
            m = int(r.group(1)) * 60 + int(r.group(2))
        else:
            r = re.search( r'^(\d+)分', tc[3] )
            if ( r != None ):
                m = int(r.group(1))
            else:
                m = 1440  #  既不是xx时xx分又不是xx分则设为1440分钟
        r = re.search( r'^(\d+\.*\d*)GB', tc[4] )  #  解析种子大小
        if ( r == None ):
            continue  #  此处判断是否为有效行
        else:
            g = float(r.group(1))
        try:
            if ( ( m < pt_site['torrentpublishtime'] ) and ( g > pt_site['torrentsize'] ) and ( int(tc[5]) == 1 ) ):  #  种子提取条件，一般发布2小时内且大于40G且只有一个源上传
                if ( log_content.find( torrenturl + '\t' ) < 0 ):  #  比对是否曾经提取过该种子
                    content += '\n' + torrenturl + '\t' + torrentname + '..' + tc[3] + '..' + tc[4] + '..' + tc[5] + '..' + tc[6] + '..' + tc[7]
        except:  #  tc[5]转整数有可能失败，不规范种子数据打出来
            WriteLog( 1, torrenturl )  #  注释加到这突然想到传递参数应该加默认值，懒得改了凑合看吧
            continue
    if ( content == '' ):  #  这个站没晒到种子也要说一下，不然看日志以为程序死了
        WriteLog( 1, pt_site['address'] + ' nothing found.' )
    mail_content += content  #  各个站提取的种子累加到这个变量里
if ( mail_content != '' ):  #  发邮件
    WriteLog( 0, 'found torrents:' + mail_content )
    mail_host = ''  #  邮箱smtp服务器地址
    mail_user = ''  #  邮箱用户名
    mail_pass = ''  #  邮箱密码
    message = MIMEText( mail_content, 'plain', 'utf-8')
    message['from'] = mail_user
    message['to'] = mail_user
    message['subject'] = 'got torrent(s) for downloading'
    try:
        smtpObj = smtplib.SMTP_SSL( mail_host, 465 )
        smtpObj.login( mail_user, mail_pass )
        smtpObj.sendmail( mail_user, mail_user, message.as_string() )
        smtpObj.quit()
        WriteLog( 1, 'mail sent.' )
    except:
        WriteLog( 1, 'smtp failed.' )
exit()
