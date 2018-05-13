# PT_Assistant
to help people sign in on a PT website, pull torrents to their email automatically.

这个程序目前可以在windows及mac osx环境下运行，可以做到以下功能

1. 利用事先保存的cookie自动登录多个pt站，避免长时间不登录被删号
2. 自动签到得魔力
3. 自动搜索种子页面的免费种，根据事先设置的筛选条件（发布时间种子大小上传人数等）提取种子，发到指定的邮箱中

安装过程详细说明：

无论在mac osx，还是windows环境下运行，都是按先以下步骤操作：

1. 创建一个目录
2. 下载最新版本的源码到刚创建的目录
3. 使用文本编辑器编辑两个json文件：
  4.1. pt_sites.json，对于ourbits, hdhome, gztown, tvhome这四个站把自己的登录cookie加进去就行了，别的pt站没邀请进不去所以没测试，理论上应该无需改动，按注释填写内容即可
    "address": 站点url地址，需以/结尾
    "torrents": 种子页面分地址
    "attendance": 签到页面分地址
    "torrentstablekey": 种子页面里种子表搜寻关键字，一般不用修改
    "headers": {"Referer":} 跟上面address字段保持一致，后面加torrents.php，假装刚从种子页面跳转过来
    "headers": {"Cookie":} 登录cookie，需用chrome浏览器抓取
    "headers": {"Host":} 跟上面address字段保持一致，注意格式，要掐头去尾
    "torrentpublishtime": 筛选条件之种子发布时间，单位分钟，筛选发布时间小于此值的种子
    "torrentsize": 筛选条件之种子大小，单位GB，筛选大于此值的种子
    "seekers": 筛选条件之做种者数量，筛选小于等于此值的种子
    "welcomeback": “欢迎回来”
    "nsigned": "签到已得"
    "signed": "签到得魔力"
    以上三字段配合使用，用于判断是否有效页面，是否需签到，一般无需修改
    自行增加pt站点时，对于NexusPHP类站点，理论上只需修改address, headers:{Referer, Cookie, Host}这四个字段，以及torrentpublishtime, torrentsize, seekers这三个筛选条件即可
  4.2. pt_init.json，改为自己的邮箱smtp服务器信息，用户名，及密码
    "debug": 日志记录级别，可以设成0，1，2，数值越小日志内容越简单
    "interval": 轮询间隔，单位秒，docker版专用，mac和win不必理会
    “ndisturb": 免打扰时段，0~23之间的任意整数，设置之后在此时段内不轮询
    "mail_host": 此字段开始往下是smtp邮件服务器设置，按需设置
5. 去python官网下载最新版的python3，安装到mac osx或windows10系统中
6. 在终端命令行方式，用pip下载第三方requests库，这两步不会的可以自己去百度，这里不细说
7. 安装完毕后还是在终端命令行状态确认一下能够进入python3，出现'>>>'提示符后，输入'import requests'命令，按回车键后未出现错误提示，能到这步说明python环境已经搭建成功
8. 输入‘exit()命令回车，退出python回到命令行

根据系统环境不同，接下来的操作过程也不相同，接下来我分别介绍windows，及mac osx环境的具体安装方法

mac osx：
9. 还是在终端命令行状态下，输入'python3 pt.py'回车，确定程序可以正常运行
10. 正常运行没有大段报错，说明前面的步骤都没问题了，如果有大段报错，请回到前面第一步仔细检查看有什么地方有疏漏
11. 执行sudo crontab -e，把下面第12步的这段写进去，其中python3的绝对路径可以用'which typhon3'确认，pt.py的绝对路径就是自己第一步创建的那个目录，ptx.log是存放运行错误日志的，路径及文件名可以自己起，或者不写也行
12. */6 * * * * /Library/Frameworks/Python.framework/Versions/3.6/bin/python3 /Users/Ben/python/pt.py >>/Users/Ben/python/ptx.log 2>&1
13. ':wq'保存退出，程序就可以运行起来了，进入程序目录，耐心等下次运行结束后，会创建pt.log文件，记录找到的种子以及签到得魔力信息，再次运行找到的种子会先跟log文件中的内容比对，新种子才发邮件。

windows：
9. 下载pt.bat到当前目录，还是在终端命令行状态下，输入'pt'回车，确定程序可以正常运行
10. 运行结束后，看是不是多了两个log文件，打开ptx.log看里面有没有大段报错，没有的话说明前面的步骤都没问题了，如果有大段报错，请回到前面第一步仔细检查看有什么地方有疏漏
11. 确认Task Scheduler服务运行起来了，再确认当前登录的windows用户是带密码的账户，这两点必须满足才能成功的加入任务计划
12. 进入任务计划程序，创建基本任务，起名后一路下一步，到启动程序这步，写入绝对路径让系统运行pt.bat批处理程序，勾选打开此任务的属性对话框后点完成
13. 进入属性设置里面，把程序设成每10分钟运行一次，程序就可以运行起来了，进入程序目录，耐心等下次运行结束后，会把运行信息写入ptx.log，新找到的种子以及签到得魔力信息会写入pt.log，找到种子后会先跟文件中的内容比对，新种子才发邮件。
