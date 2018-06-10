# coding=utf-8

"""  
Created on 2016-01-09 @author: Eastmount

功能: 爬取新浪微博用户的信息
信息：用户ID 用户名 注册时间 性别 地址(城市) 是否认证 用户标签(明星、搞笑等信息)
    个人资料完成度 粉丝数 关注数 微博数 粉丝ID列表 关注人ID列表 特别关注列表
网址：http://weibo.cn/ 数据量更小 相对http://weibo.com/

参考：佳琪学弟和datahref博客 使用Selenium获取登录新浪微博的Cookie
java链接：http://datahref.com/book/article.php?article=webcollector_WeiboCrawler 
python：http://blog.csdn.net/warrior_zhang/article/details/50198699
"""    

import time            
import re            
import os    
import sys  
import codecs  
import shutil
import urllib 
from selenium import webdriver        
from selenium.webdriver.common.keys import Keys        
import selenium.webdriver.support.ui as ui        
from selenium.webdriver.common.action_chains import ActionChains


#先调用无界面浏览器PhantomJS或Firefox    
#driver = webdriver.PhantomJS(executable_path="G:\phantomjs-1.9.1-windows\phantomjs.exe")    
driver = webdriver.Firefox()    
wait = ui.WebDriverWait(driver,10)


#全局变量 文件操作读写信息
infofile = codecs.open("fs.txt", 'a', 'utf-8')
all = codecs.open("all.txt", 'r+', 'utf-8')
graph=codecs.open("graph.txt",'a','utf-8')
yipa=codecs.open("yipa.txt",'r+','utf-8')
id=[]
id1=[]
m=0
#********************************************************************************
#                  第一步: 登陆weibo.cn 获取新浪微博的cookie
#        该方法针对weibo.cn有效(明文形式传输数据) weibo.com见学弟设置POST和Header方法
#                LoginWeibo(username, password) 参数用户名 密码
#********************************************************************************

# 参考：http://download.csdn.net/download/mengh2016/7752097
# 不会出现WebDriverException: Message: 'Can\'t load the profile: 的Firefox＆selenium python版本

def LoginWeibo(username, password):
    try:
        #**********************************************************************
        # 直接访问driver.get("http://weibo.cn/5824697471")会跳转到登陆页面 用户id
        #
        # 用户名<input name="mobile" size="30" value="" type="text"></input>
        # 密码 "password_4903" 中数字会变动,故采用绝对路径方法,否则不能定位到元素
        #
        # 勾选记住登录状态check默认是保留 故注释掉该代码 不保留Cookie 则'expiry'=None
        #**********************************************************************
        
        #输入用户名/密码登录
        print (u'准备登陆Weibo.cn网站...')
        driver.get("https://passport.weibo.cn/signin/login")
        time.sleep(20)
        elem_user = driver.find_element_by_xpath("/html/body/div[1]/form/section/div[1]/p/input")
        elem_user.send_keys(username) #用户名
        elem_pwd = driver.find_element_by_xpath("/html/body/div[1]/form/section/div[2]/p/input")
        elem_pwd.send_keys(password)  #密码
        #elem_rem = driver.find_element_by_name("remember")
        #elem_rem.click()             #记住登录状态
        elem_sub = driver.find_element_by_name("submit")
        elem_sub.click()              #点击登陆
        time.sleep(2)
        
        #获取Coockie 推荐 http://www.cnblogs.com/fnng/p/3269450.html


        #driver.get_cookies()类型list 仅包含一个元素cookie类型dict
        print (u'登陆成功...')


    except Exception as e:
        print ("Error: ", e)
    finally:
        print (u'End LoginWeibo!\n\n')


#********************************************************************************
#                  第二步: 访问个人页面http://weibo.cn/5824697471并获取信息
#                                VisitPersonPage()
#        编码常见错误 UnicodeEncodeError: 'ascii' codec can't encode characters 
#********************************************************************************
def VisitPersonPage(user_id):
    try:
        global infofile,m,dayinid,id1
        global inforead,dayinname,listfile,id,m
        print (u'准备访问个人网站.....')

        driver.get("http://weibo.cn/" + user_id)

        #**************************************************************************
        # No.1 直接获取 用户昵称 微博数 关注数 粉丝数
        #      str_name.text是unicode编码类型
        #**************************************************************************

        #用户id
        print (u'个人详细信息')
        print ('**********************************************')
        print (u'用户id: ' + user_id)
        
        str_fs = driver.find_element_by_xpath("//div[@class='tip2']/a[2]")
        pattern = r"\d+\.?\d*" 
        guid = re.findall(pattern, str_fs.text, re.M)
        num_fs = int(guid[0])
        print (u'粉丝数: ' + str(num_fs))

        #***************************************************************************
        # N0.2 点击详细资料 在获取用户基本信息 性别 地址 生日 标签
        #      获取属性方法[重点] get_attribute("href") 或者url+id+info/..
        #      在No.1调用方法就可以获取url 我主要感觉这样排版更易懂直观才放在No.2
        #***************************************************************************

        #详细资料url http://weibo.cn/5824697471/info
        print (u'\n获取相关URL：')
        info = driver.find_element_by_xpath("//div[@class='ut']/a[2]")  #资料 个人[详细资料]
        url_info = info.get_attribute("href")
        url_wb = "http://weibo.cn/" + user_id + "/profile"
        info = driver.find_element_by_xpath("//div[@class='tip2']/a[1]")
        url_gz = info.get_attribute("href")

        #输出url
        print url_info
        print url_wb
        print url_gz


        infofile.write(user_id+" "+ str(num_fs) + '\r\n')
        
        #***************************************************************************
        # No.4 获取关注人列表
        #***************************************************************************

        print u'\n关注人列表信息:' 
        driver.get(url_gz)
        info = driver.find_element_by_xpath("//div[@id='pagelist']/form/div")
        #print info.text            #下页  1/20页
        pattern = r"\d+\.?\d*"     #获取第二个数字 
        guid = re.findall(pattern, info.text, re.S|re.M)
        num_page = int(guid[1])
        #print 'Page: ', num_page
        print '**********************************************'


        #文件写入关注列表人id

        

        #获取关注人列表
        i = 1
        gz_urls = []
        while i <= num_page:
            count1 = 0
            count2=0
	    count3=0
            gz_nums = []
            url = url_gz + '?page=' + str(i)
            #print url
            driver.get(url)
            info1 = driver.find_elements_by_xpath("/html/body/table/tbody/tr/td[2]")
            for value in info1:
                count1 += 1
                fs=re.findall("\d+",value.text) 
                if len(fs)>1:
		    if int(fs[1])>5000000:
                        gz_nums.append(count1)
                else:
                    if int(fs[0])>5000000:
                        gz_nums.append(count1)
	    info = driver.find_elements_by_xpath("/html/body/table/tbody/tr/td[2]/a[1]")
            for value in info:
                count2 += 1
                url = value.get_attribute("href")
                gz_urls.append(url)
                url_id = url.split("/")[-1]    
                if count2 in gz_nums:      
                    graph.write(user_id+','+url_id+'\r\n')            
                    if url_id not in id1:
                        id1.append(url_id)
                        all.write(url_id + '\r\n')               
            #增1
            i = i + 1 
        print '**********************************************'
        
        
        

        

    except Exception , e:      
        print "Error: ",e
    finally:    
        print u'VisitPersonPage!\n\n'
        print '**********************************************\n'
        

    
#*******************************************************************************
#                                程序入口 预先调用
#*******************************************************************************
    
if __name__ == '__main__':

    #定义变量

    #user_id = '2778357077'             #用户id url+id访问个人
    #user_id = 'renzhiqiang'
    #user_id = 'guangxianliuyan'  #柳岩
    #'renzhiqiang' 任志强

    id2=[]
    id1=[]
    data=yipa.read()
    data=data.split('\r\n')
    print data
    for da in data:
        id2.append(da)
    data1=all.read()
    data1=data1.split('\r\n')
    for da in data1:
        id1.append(da)
    print u"数据载入完毕"

    LoginWeibo("13946518542", "hys//123")      #登陆微博

    #id1.append("realchenxiao")
    
    #SyntaxWarning: name 'inforead' is assigned to before global declaration
    #参考:stackoverflow
    #在if __name__ == '__main__':引用全局变量不需要定义 global inforead 省略即可
    print u'开始爬取:'
    for idd in id1:                #访问个
        if idd not in id2:           
            VisitPersonPage(idd)  
            id2.append(idd)
            yipa.write(idd+"\r\n")
       
    infofile.close()
    all.close()
    graph.close()
    yipa.close()
    
