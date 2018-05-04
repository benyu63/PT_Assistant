# PT_Assistant
to help people sign in on a PT website, pull torrents to their email automatically.

这个程序可以做到以下功能

1. 利用事先保存的cookie自动登录多个pt站，避免长时间不登录被删号
2. 自动签到得魔力
3. 自动搜索种子页面的免费种，根据事先设置的筛选条件（发布时间种子大小上传人数等）提取种子，发到指定的邮箱中

在mac osx下面运行，挂到cron里面，每6分钟执行一次，从昨天晚上到现在没出问题。

使用之前需要编辑两个地方：
1. 编辑程序开始处PT_Sites这个结构，对于ourbits, hdhome, gztown, tvhome这四个站把自己的登录cookie加进去就行了，别的pt站没邀请进不去所以没测试
2. 编辑程序结尾处的邮件服务器登录信息，我是在smtp.qq.com上调试的

运行前为方便，先把文件名里面的数字去掉，改为pt.py，cron里面做如下设置

*/6 * * * * /Library/Frameworks/Python.framework/Versions/3.6/bin/python3 /Users/Ben/python/pt.py >>/Users/Ben/python/ptx.log 2>&1

输出重定向文件名可以随意起，不影响运行

程序运行起来后，会在程序所在目录创建pt.log文件，记录找到的种子以及签到得魔力信息，再次运行找到的种子会先跟log文件中的内容比对，新种子才发邮件。
