#!/usr/bin/python3
# -*- coding:utf-8 -*-
import random
import smtplib
import datetime
import logging
import time
import json
import os
import re
import requests
from email.mime.text import MIMEText

#  全局变量
global mylog
global filepath
global PT_Init

#  函数
def GetHTML( url, headers, encoding ):
    time.sleep( random.uniform( 2, 4 ) )
    try:
        requests.packages.urllib3.disable_warnings()  #  关https警告
        r = requests.get( url, headers=headers, verify=False )
        r.encoding = encoding
        return( r.text )
    except:
        return( '' )

def ExtractDownloadHref( html ):  #  提取种子的超链接
    m = re.search( r'<a.+href=[\'"](download\.php[^\'"]+)[\'"]', html )
    if ( m == None ):
        return( '' )
    else:
        return( m.group(1) )

def ExtractHTML( name, s1, s2, html ):  #  配对s1+name|s2标签，提取该标签中所有内容，可处理嵌套结构
    l = len( html[0] )
    ls1 = len( s1 )
    ls2 = len( s2 )
    p1 = html[0].find( s1 + name )
    if ( p1 < 0 ):
        return( '' )
    c = 1
    p2 = p1 + ls1 + len(name)
    while ( c > 0 ):
        p3 = html[0][p2:].find( s1 )
        p4 = html[0][p2:].find( s2 )
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
            name = html[0][p1:]
            html[0] = html[0][:p1]
            return( name )
    name = html[0][p1:p2]
    s1 = html[0][:p1]
    s2 = html[0][p2:]
    html[0] = s1 + s2
    return( name )

def StripallTags( html ):  #  剥除所有标签
    html = re.sub( r'<[\s]*?script[^>]*?>[\s\S]*?<[\s]*?\/[\s]*?script[\s]*?>', '', html )
    html = re.sub( r'<[\s]*?style[^>]*?>[\s\S]*?<[\s]*?\/[\s]*?style[\s]*?>', '', html )
    html = re.sub( r'<[^>]*>', '', html )
    html = html.replace( '&nbsp;', ' ' )
    html = html.replace( '&#160;', ' ' )
    html = html.replace( '&quot;', '"' )
    html = html.replace( '&amp;', '&' )
    html = html.replace( '&lt;', '<' )
    html = html.replace( '&gt;', '>' )
    html = re.sub( r'[\t\f\v\r ]+', ' ', html )
    html = re.sub( r'( *\n+ *)+', r'\n', html )
    html = re.sub( r'^([ \n]+)+|([ \n]+)+$', '', html )
    html = re.sub( r'\n', '<br>', html )
    return( html )

def main():
    global filepath
    global PT_Init
    pstr1 = ['']
    pstr2 = ['']
    ml = {'T':1024,'G':1,'M':0.0009766,'K':0.0000009}

    try:    #  读取站点信息文件
        f = open( filepath + PT_Init['sitesfilename'], 'r', encoding=PT_Init['encoding'] )
        PT_Sites = json.load( f )
        f.close()
    except:
        mylog.error( 'could not load the sites file.' )
        return

    try:    #  读取种子日志文件
        f = open( filepath + PT_Init['torrentslogname'], 'r', encoding=PT_Init['encoding'] )
        torrents_log = f.read()
        f.close()
    except:
        mylog.debug( 'could not read the torrents log file.' )
        torrents_log = ''

    mylog.debug( 'initialize .. done.' )
    torrents_found = ''         #  每个站筛出的种子累加到这里
    for pt_site in PT_Sites:    #  根据上面的数据结构循环遍历各pt站
        url = pt_site['address'] + pt_site['torrents']
        headers = pt_site['headers']
        encoding = pt_site['encoding']
        html = GetHTML( url, headers, encoding )#  读取种子页面
        if ( html == '' ):      #  读取失败
            continue
        content = StripallTags( html )          #  剥除所有标签，便于比对，不剥也没事
        b = ( content.find( pt_site['signed'] ) >= 0 )  #  三个条件的逻辑判断
        b = ( b << 1 ) | ( content.find( pt_site['nsigned'] ) >= 0 )
        b = ( b << 1 ) | ( content.find( pt_site['welcomeback'] ) >= 0 )
        if ( ( b != 3 ) and ( b != 5 ) ):       #  处理非正常页面
            mylog.warning( url + ' wrong page, check the url and the cookies plz' )
            mylog.debug( content )
            continue
        if ( b == 3 ):                      #  需要签到
            url = pt_site['address'] + pt_site['attendance']
            headers = pt_site['headers']
            encoding = pt_site['encoding']  #  读取签到页面
            html = GetHTML( url, headers, encoding )
            content = StripallTags( html )
            matcher = re.search( pt_site['signed']+'\d*', content )
            if ( matcher != None ):         #  签到成功
                mylog.info( pt_site['address'] + ' ' + matcher.group( 0 ) + '魔力' ) 
                url = pt_site['address'] + pt_site['torrents']
                headers = pt_site['headers']
                encoding = pt_site['encoding']
                html = GetHTML( url, headers, encoding )  #  重新读取种子页面
                content = StripallTags( html )
            else:
                mylog.warning( url + ' something might be wrong, \'ll sign next round' )
                mylog.debug( content )
                continue

        pstr1[0] = html
        pstr1[0] = ExtractHTML( pt_site['torrentstablekey'], '<table', '/table>', pstr1 )  #  提取种子表
        if ( pstr1[0] == '' ):
            mylog.warning( url + ' could not extract the torrents table.' )
            mylog.debug( content )
            continue
#        mylog.debug( 'start looking for the torrents in it.' )
        c1 = 0; c2 = 0; c3 = 0
        content = ''  #  找到的种子存在这里
        for i in range(100):  #  前100个种子
            pstr2[0] = ExtractHTML( r'', r'<tr', r'/tr>', pstr1 )  #  种子表里提取1行
            tc = ['' for j in range(8)]
            for j in range(8): tc[j] = ExtractHTML( r'', r'<td', r'/td>', pstr2 )  #  1行里提取8列
            torrenturl = pt_site['address'] + ExtractDownloadHref( tc[1] )
            for j in range(8): tc[j] = StripallTags( tc[j] )
            if ( ( tc[1] == '' ) or ( tc[3] == '' ) or ( tc[4] == '' ) or ( tc[5] == '' ) ): continue
            tc[0] = ''
            for j in range(1,8): tc[0] += '..' + tc[j]
            try:
                m = 0
                r = re.search( r'^((\d+)天)?((\d+)时)?((\d+)分)?', tc[3] )  #  解析发种时间
                if ( r.group(2) != None ): m += int(r.group(2))*60*24
                if ( r.group(4) != None ): m += int(r.group(4))*60
                if ( r.group(6) != None ): m += int(r.group(6))
                if ( m == 0 ): m = 45000
                r = re.search( r'^(\d+\.*\d*)([TGMK])B', tc[4] )  #  解析种子大小
                g = float(r.group(1)); g*= ml[r.group(2)];
                s = int(tc[5])
            except:
                mylog.info( 'wrong torrent' + tc[0] )
                continue
            #  种子提取条件，一般发布2小时内且大于40G且只有一个源上传
            c1 += 1
            if ( ( m <= pt_site['torrentpublishtime'] ) and ( g >= pt_site['torrentsize'] ) and ( s <= pt_site['seekers'] ) ):
                c2 += 1
                tc[0] = torrenturl + '\t' + tc[0]
                if ( torrents_log.find( torrenturl + '\t' ) < 0 ):  #  比对是否曾经提取过该种子
                    content += tc[0] + '\n'
                    c3 += 1
        mylog.debug( str(c1) + ':' + str(c2) + ':' + str(c3) )
        torrents_found += content  #  各个站提取的种子累加到这个变量里
    #  循环结束
    if ( torrents_found == '' ):
        mylog.info( 'found nothing new.' )
        return
    #  种子发邮件
    message = MIMEText( torrents_found, 'plain', 'utf-8')
    message['subject'] = PT_Init['subject']
    message['from'] = PT_Init['from']
    message['to'] = PT_Init['to']
    try:
        if ( PT_Init['mail_ssl'] != 0 ):
            smtpObj = smtplib.SMTP_SSL( PT_Init['mail_host'], 465 )
        else:
            smtpObj = smtplib.SMTP()
            smtpObj.connect( PT_Init['mail_host'], 25 )
        smtpObj.login( PT_Init['user'], PT_Init['pass'] )
        smtpObj.sendmail( message['from'], message['to'], message.as_string() )
        smtpObj.quit()
    except:
        mylog.warning( 'mail send failure.' )
        return
    #  种子写日志
    try:
        f = open( filepath + PT_Init['torrentslogname'], 'a', encoding=PT_Init['encoding'] )
        f.write( str( datetime.date.today() ) + ' ' + time.strftime('%H:%M:%S') + '\n' + torrents_found )
        f.close()
    except:
        mylog.warning( 'wrote torrents log file failure.' )
        return
    mylog.info( 'torrents were mailed and written into the log file.' )
    return

#  程序起点
if ( os.path.sep == '\\' ): #  获取绝对路径及系统编码
    filepath = re.sub( r'[^\\]+$', '', os.path.abspath(__file__) )
else:   #  Windows目录分隔符跟Linux不同，必须分别处理
    filepath = re.sub( r'[^/]+$', '', os.path.abspath(__file__) )

logging.basicConfig( format='[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%H:%M', level=logging.DEBUG )
mylog = logging.getLogger()

while ( True ):
    log_level = ( logging.WARNING, logging.INFO, logging.DEBUG )
    try:            #  读取初始化文件
        f = open( filepath + 'pt_init.json', 'r', encoding='utf-8' )
        PT_Init = json.load( f )
        f.close()   #  设置日志记录等级
        mylog.setLevel( log_level[int(PT_Init['debug']%3)] )
        now = datetime.datetime.now()
        for i in PT_Init['ndisturb']:
            if ( i == now.hour ):
                i = 24
                break
        c = int( PT_Init['interval'] )
    except:         #  如读取失败等120秒后再试
        mylog.error( 'could not load the [' + filepath + 'pt_init.json] file, \'ll try again after 2 minutes.' )
        time.sleep( 120 )
        continue
    if ( i == 24 ): #  判断当前是否处于免打扰时间段
        mylog.info( 'bed time .. no disturbing .. \'ll be back in 30 minutes.' )
        time.sleep( 1800 )
    else:
        main()
        time.sleep( c )
