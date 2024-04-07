#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
Program:        doaxvv_auto
Version:        0.8.2
Description:这个脚本用来给doaxvv挑战赛挂机
        1.按下数字键1自动刷鼠标所在位置的挑战，体力耗尽为止
        2.按下数字键2自动刷鼠标所在位置的挑战，体力耗尽自动补水
        3.按下数字键3，自动补水+自动验证码，长期运行
        4.按下数字键4，大跳进行游戏
        5.按下数字键5，自动抽绿点，抽完为止
        6.按下数字键6，21点算牌
        7.按下数字键7，计算抽卡概率
        8.按下数字键8，显示详细帮助页面
        9.按下小键盘9强制终止运行
        10.暂只支持1080P
TODO:   
        a.*****测试验证码功能！！！******
        b.完善gui界面（为了防止检测暂时不做）
        c.能够完成系列挑战赛及随机挑战赛
        d.提高速度（为了防止检测暂时不做）
        e.多分辨率
        f.封装脚本的方法
        g.LOG日志
Date: 2022.4.24
Author: Chaobs
Update Log:
2022.4.24： 添加了判断是否进入战斗中函数，修复了网速波动时出错的bug
            如果没有开跳过会自动开启
            异常模块仍然没有解决
2022.4.23： 从本版本起改用VSCode编辑器。
            考虑后续通过git管理版本。
            将keyboard模块复制到了本地，方便对winkeyboard在捕捉到异常时的处理（重新抛出）
            在主要挂机工作结束后，用return返回而非调用stopfarm()强制结束。
2022.4.19： 实装了21点算牌功能和帮助菜单。
            现在按下终止后，出发自定义异常，回到主线程(失败)
2022.4.18：实装抽绿点、大跳功能
2022.4.16： 优化了从自方法跳转到主程序的逻辑。这样结束后不用手动再次打开程序了
            增加了抽绿点的功能
            增加了概率计算器
2022.4.12： 优化了模块导入
2022.4.12： 完善了进程伪装，修复了打包为EXE文件后的库缺失，加入了管理员权限获取，提升稳定性。
            验证码模块仍然待测试
2022.4.11： 修改了水耗尽时不能终止的bug，优化了第三方库函数的导入，方便用PyInstaller打包
2022.4.10: 实现了验证码自动填充功能（实验中）。进程伪装。
2022.4.10: 修复了发现不了验证码框的问题
2022.4.9： 新增发现验证码检测页面的功能，暂时只能发现了就退出，ocr部分没有处理好
2022.4.9： 实现了完整的自动补水功能
2022.4.8： 优化了一些有规律的操作，让它看起来更随机，修改了坐标的小bug
2022.4.8： 进程伪装
2022.4.8： 大幅改进防检测机制
2022.4.7： 0.3.0优化了挂机逻辑，现在会根据检测到的页面判断下一步行为。
            更改了鼠标移动参数，防检测。
            半自动补水（水不足时无法处理）
2022 4.6： 0.2.0优化了挂机逻辑，增加了按键提示
2022.4.6： 0.1.0自动挂机，已经可以简单使用代替游戏自带的autoplay了
2022.4.5： 0.0.1半自动挂机，需要手动切换窗口
'''

#版本号
VERSION = 'v0.8.2'

#pyautogui处理鼠标，keyboard从键盘接收消息，time和random用来防检测,os终止程序
#ddddocr处理验证码，setproctitle伪装进程
#ctypes和sys用来让程序提升到管理员权限
#goto处理进程跳转
from pyautogui import moveTo, easeInQuad, easeOutQuad, easeInOutQuad, easeInBounce, linear, pixel, click, write, position, screenshot, FailSafeException
from time import sleep
from random import randint, uniform, choice, random
from keyboard import hook_key, add_hotkey, wait, unhook_all, send
from os import remove, _exit, system
from ddddocr import DdddOcr
from setproctitle import setproctitle
from ctypes import windll
from sys import executable

#屏幕尺寸及中间点
SCREEN_SIZE=(1920,1080)
MID_POINT=(960,540)

#固定1080P下一些按钮的位置
#1080P下开始比赛的位置
START_XY=(1600,1000)

#跳过的位置
SKIP_XY=(1510,1030)
SKIP_CONFIRM_XY=(1070,870)#确认跳过

#下面的四组数据描述主页面的四个点和颜色
#如果这四个特征点都符合则证明游戏回到了挑战赛主页面
MAIN_A=(1464, 39)
MAIN_B=(1469, 38)
MAIN_C=(1708, 5)
MAIN_D=(1606, 113)
A_COLOR=(57, 231, 115)
B_COLOR=(82, 235, 123)
C_COLOR=(74, 178, 246)
D_COLOR=(255, 255, 255)

#以下几个点用于描述验证码页面
#验证码图片条的坐标还需要测试
CAP_A=(865, 285)
CAP_B=(774, 308)
CAP_C=(928, 413)
CAP_A_COLOR=(255, 0, 0)
CAP_B_COLOR=(255, 251, 206)
CAP_C_COLOR=(255, 251, 255)
CAP_CONFIRM=(1070, 880)
CAP_PLACE=(((680, 400),(1240, 510))) #验证码框的位置
CAP_REGION=(680, 400,560,110) #左上角顶点在(680, 400)的560x110区域

#下面的三组数据用于判断是否需要补充
#以及补水和确定按钮的位置
FP_A=(1155, 610)
FP_B=(1192, 331)
FP_C=(713, 592)
FP_A_COLOR=(49, 93, 247)
FP_B_COLOR=(255, 251, 206)
FP_C_COLOR=(0, 48, 66)
FP_PLUS=(890, 710)
FP_OK=(1055, 900)
FP_100=(888, 598) #恢复100体力的水

#下面几个点用来对抽绿点的位置
#以及绿点不足了停止运行进行判断
GREEN_START = (1325, 815)
GREEN_OK = (1073, 875)
GREEN_OPEN= ((1198, 215),(1737, 847))
GREEN_SKIP = ((375, 288),(859, 796))
GREEN_RESTART = (1617, 779)
GREEN_A=(1231, 30)
GREEN_B=(1469, 39)
GREEN_C=(1709, 38)
GREEN_A_COLOR=(231, 85, 165)
GREEN_B_COLOR=(82, 235, 123)
GREEN_C_COLOR=(140, 125, 189)
ZEROGREEN_A = (1028, 327)
ZEROGREEN_B = (1085, 333)
ZEROGREEN_C = (881, 551)
ZEROGREEN_D = (1060, 864)
ZEROGREEN_A_COLOR = (229, 0, 0)
ZEROGREEN_B_COLOR = (255, 251, 206)
ZEROGREEN_C_COLOR = (82, 73, 74)
ZEROGREEN_D_COLOR = (214, 251, 255)

#检测是否没有水了
NONEFP_A=(1028, 308)
NONEFP_B=(654, 356)
NONEFP_C=(852, 528)
NONEFP_A_COLOR=(229, 0, 0)
NONEFP_B_COLOR=(255, 251, 206)
NONEFP_C_COLOR=(177, 233, 236)

#下面三个点用来判断是否进入了战斗画面
BATTLE_A=(236, 58)
BATTLE_B=(1659, 59)
BATTLE_C=(1669, 70)
BATTLE_A_COLOR=(109, 145, 207)
BATTLE_B_COLOR=(111, 146, 222)
BATTLE_C_COLOR=(216, 230, 118)

#下面的一个点用来对自动跳过按钮进行检测
AUTOON_BUTTON = (1430, 896)
AUTOON_BUTTON_COLOR = (239, 243, 255)

#下面的三组数据用于判断是否进入结果页面
RESULT_A=(822, 664)
RESULT_B=(771, 527)
RESULT_C=(1116, 595)
RESULT_A_COLOR=(255, 174, 214)
RESULT_B_COLOR=(255, 255, 255)
RESULT_C_COLOR=(255, 255, 255)

#屏幕上几个没有太多实际作用的空闲点
IDLE_A = (420, 840)
IDLE_B = (810, 900)
IDLE_C = (710, 130)

#模式1：体力耗尽自动停止，模式2：自动补水
#模式3：补水+验证码（验证码只会在长时间挂机时出现）
#模式4：大跳进行游戏，不补水
FARM_MODE_1=1
FARM_MODE_2=2
FARM_MODE_3=3
FARM_MODE_4=4

#鼠标随机化的程度，即相对于目标点飘离的程度
#补水小按钮页面需要随机化程度低
#假动作需要的随机化程度高
RAND_LOW = 10
RAND_MID = 20
RAND_HIG = 30
RAND_SUP = 50


#随机化鼠标位置
def rollplace(x, level):
    a= (randint(x[0]-level,x[0]+level), randint(x[1]-level,x[1]+level))
    return a
    
#用于随机化鼠标移动路径
#确定鼠标将要移向的终点，中间的路程随机
def feint_move(x,t,level):
    '''x是一个包含横纵坐标的元组，t是最短需要的时间，level是随机化程度'''
    i = randint(0,3) #随机化最多三个点
    while i>0 :
        a = randint(0,SCREEN_SIZE[0]-1)
        b = randint(0,SCREEN_SIZE[1]-1)
        moveTo(a,b,duration=uniform(0.5,2),tween=choice([easeInQuad,easeOutQuad,easeInOutQuad,easeInBounce,linear])) #几种不同的运动函数移动位置
        i = i - 1
    x = rollplace(x,level)
    moveTo(x[0],x[1],duration=t, tween=linear) #最后移动到目标点
    sleep(random()) #随机暂停0~1秒
    return
    
#用于在没有操作的时候，在指定时间内制造随机的轨迹
#比如等待结果、加载的过程中随机移动鼠标
def idle_move(t):
    '''t是指定的时间'''
    i = randint(1,3)
    while i > 0:
        a = randint(0,SCREEN_SIZE[0]-1)
        b = randint(1,SCREEN_SIZE[1]-1)
        moveTo(a,b,duration=t / i,tween=choice([easeInQuad,easeOutQuad,easeInOutQuad,easeInBounce,linear])) #几种不同的运动函数移动位置
        i = i - 1
    sleep(random()) #随机暂停0~1秒
    return
    
#判断是否在挑战赛主页面的函数
def isMain():
    '''根据主页面的四个点的颜色，判断是否返回了主页面'''
    a=pixel(MAIN_A[0],MAIN_A[1])
    b=pixel(MAIN_B[0],MAIN_B[1])
    c=pixel(MAIN_C[0],MAIN_C[1])
    d=pixel(MAIN_D[0],MAIN_D[1])
    if a==A_COLOR and b==B_COLOR and c==C_COLOR and d==D_COLOR:
        return True #是主页面
    else:
        return False
    
#判断是否缺水的函数
def isTired():
    '''缺少体力则弹出添加体力的框，根据特征点判断是否要加水'''
    a=pixel(FP_A[0],FP_A[1])
    b=pixel(FP_B[0],FP_B[1])
    c=pixel(FP_C[0],FP_C[1])
    if a==FP_A_COLOR and b==FP_B_COLOR and c==FP_C_COLOR:
        return True #缺水
    else:
        return False
        
#检测是否没有水的函数
def isNonewater():
    a=pixel(NONEFP_A[0],NONEFP_A[1])
    b=pixel(NONEFP_B[0],NONEFP_B[1])
    c=pixel(NONEFP_C[0],NONEFP_C[1])
    if a==NONEFP_A_COLOR and b==NONEFP_B_COLOR and c==NONEFP_C_COLOR:
        return True
    else:
        return False
    
#补水的函数
def charge():
    '''
    移动到全满水的位置补水，有限补充100体力的
    如果没有则补充全满水
    如果没有水了则终止脚本运行
    '''
    feint_move(FP_100,0.5,RAND_LOW)
    click(interval=random())
    feint_move(FP_PLUS,0.5,RAND_LOW)
    click(interval=random())
    feint_move(FP_OK,0.5,RAND_MID)
    click(interval=random())
    idle_move(1)
    return

#判断进入了结果结算界面的函数
def isResult():
    '''特征点还需要测试'''
    a=pixel(RESULT_A[0],RESULT_A[1])
    b=pixel(RESULT_B[0],RESULT_B[1])
    c=pixel(RESULT_C[0],RESULT_C[1])
    if a==RESULT_A_COLOR and b==RESULT_B_COLOR and c==RESULT_C_COLOR:
        return True #在结果页面
    else:
        return False
        
#判断是否需要验证的函数
def isCaptcha():
    '''根据三个特征点判断是否需要验证码'''
    a=pixel(CAP_A[0],CAP_A[1])
    b=pixel(CAP_B[0],CAP_B[1])
    c=pixel(CAP_C[0],CAP_C[1])
    if a==CAP_A_COLOR and b==CAP_B_COLOR and c==CAP_C_COLOR:
        return True
    else:
        return False

#完成图片验证的函数
def fillCaptcha():
    '''
    因为是一片会滚动的验证码
    所以需要多次截图试别，
    检查验证码位数是否是6位，然后用键盘函数写入
    如果多次未能成功试别则终止运行
    '''
    i=10
    ocr = DdddOcr() #创建ocr对象
    while i>=0: #试10次
        pic = screenshot("tmp.jpg",region=CAP_REGION) #验证码截图
        
        '''
        调试用
        '''
        input()
    
        with open("tmp.jpg", 'rb') as f: #打开截图
            image = f.read()
        res = ocr.classification(image) #文字识别
        
        if len(res)==6:
            idle_move(0.5)
            write(res, interval=random()) #将识别出来的文字写入
            feint_move(CAP_CONFIRM,1,RAND_MID) #移动到确定按钮
            click(interval=random()) #确定
            '''
            调试用
            '''
            print("验证成功！")
            return #结束验证码填写
        remove("tmp.jpg") #删除临时文件
        i= i - 1
        sleep(1)
    
    #10次之后仍没结果，结束运行
    return

#判断是否处于战斗页面的函数
def isBattle():
    '''
    True战斗画面，False非战斗画面
    '''
    a=pixel(BATTLE_A[0],BATTLE_A[1])
    b=pixel(BATTLE_B[0],BATTLE_B[1])
    c=pixel(BATTLE_C[0],BATTLE_C[1])
    if a==BATTLE_A_COLOR and b==BATTLE_B_COLOR and c==BATTLE_C_COLOR:
        return True
    else:
        return False

#判断自动跳过是否开启的函数
def isAutoon():
    '''
    检测跳过按钮最左侧，如果为白色证明是关闭的
    True开启了，False未开启
    '''
    a=pixel(AUTOON_BUTTON[0],AUTOON_BUTTON[1])
    if a == AUTOON_BUTTON_COLOR:
        return False
    else:
        return True


#强制结束挂机
def stopfarm(x):
    _exit(0)

#开始挂机
def startfarm(mode):
    '''开始挂机，mode是根据键盘传入的参数，FARM_MODE_1表示体力耗尽为止，FARM_MODE_2表示自动补水'''
    currentXY= position() #获取当前位置
    while True:
        match(currentXY,mode)
        i = choice(range(1,8)) #7分之1的概率在完成一场比赛后暂停
        if i == 1:
            sleep(uniform(2,10))
    return


#开始指定位置的一场比赛
def match(xy,mode):
    '''mode是startfarm传入的参数，FARM_MODE_1表示体力耗尽为止，FARM_MODE_2表示自动补水'''

    while not isMain(): #不在挑战赛主页面，不进入比赛
        continue
        
    feint_move(xy,0.5,RAND_LOW) #鼠标移到进入挑战赛的页面
    click(interval=random()) #进入比赛
    
    idle_move(3) #等3秒
    
    feint_move(START_XY,1,RAND_MID) #移动到挑战
    click(interval=random()) #开始比赛
    
    '''
    处理图片验证的代码，待完善，验证码和缺水同时存在
    则验证码先出现
    '''
    idle_move(1)
    if isCaptcha(): #需要验证
        if mode == FARM_MODE_3:
            fillCaptcha() #模式3填验证码
            feint_move(START_XY,1,RAND_HIG)
            click(interval=random()) #填写验证码后开始比赛
        else:
            stopfarm(3) #停止运行
    
    idle_move(2)
    if isNonewater(): #0.7.1更修修复的bug
        stopfarm(3) #没有体力水了，自动结束运行
    if isTired(): #还有库存但是缺水
        if mode==FARM_MODE_1 or mode==FARM_MODE_4: #但是不自动补水，结束挂机
            return
        elif mode==FARM_MODE_2 or mode==FARM_MODE_3: #自动补水模式
            charge()
            feint_move(START_XY,1,RAND_HIG)
            click(interval=random()) #补水后开始比赛
            idle_move(2)

    #未进入战斗画面，等待
    while not isBattle():
        continue

    #进入游戏
    #自动跳过没开启，点击开启
    if not isAutoon():
        feint_move(AUTOON_BUTTON,0.5,RAND_LOW)
        click(interval=random()) #点击开启自动跳过
    
    if mode==FARM_MODE_4:
        #大跳模式

        feint_move(SKIP_XY,1,RAND_MID)
        click(interval=random())
        feint_move(SKIP_CONFIRM_XY,0.5,RAND_MID)
        click(interval=random()) #确认跳过
    
    #用auto on模式游玩
    while not isResult():
        idle_move(3) #一直等结算页面
        
    '''结算页面的跳过参数需要调整'''
    feint_move(MID_POINT,0.5,RAND_SUP)
    click(interval=random()) #确认结果
    
    while not isMain():
        feint_move(choice([IDLE_A,IDLE_B,IDLE_C]),1.5,RAND_MID)
        click(interval=random())
        
    feint_move(choice([IDLE_A,IDLE_B,IDLE_C]),0.5,RAND_SUP) #在4个空闲点之间徘徊
    idle_move(2.5)
    if choice([1,2,3,4,5,6])==6: #六分之一的概率在一次比赛结束后休息0.5~5秒钟
        sleep(uniform(0.5,5))
    return

#判断还有没有绿点的函数
def isZerogreen():
    a=pixel(ZEROGREEN_A[0],ZEROGREEN_A[1])
    b=pixel(ZEROGREEN_B[0],ZEROGREEN_B[1])
    c=pixel(ZEROGREEN_C[0],ZEROGREEN_C[1])
    d=pixel(ZEROGREEN_D[0],ZEROGREEN_D[1])
    if a==ZEROGREEN_A_COLOR and b==ZEROGREEN_B_COLOR and c==ZEROGREEN_C_COLOR and d==ZEROGREEN_D_COLOR:
        return True
    else:
        return False
    
#判断是否在扭蛋界面的函数
def isGacha():
    '''
    返回True说明在抽卡页面可以进行下一步
    '''
    a=pixel(GREEN_A[0],GREEN_A[1])
    b=pixel(GREEN_B[0],GREEN_B[1])
    c=pixel(GREEN_C[0],GREEN_C[1])
    if a==GREEN_A_COLOR and b==GREEN_B_COLOR and c==GREEN_C_COLOR :
        return True
    else:
        return False
    
#抽绿点的函数
def greenpoint():
    feint_move(GREEN_START,0.5,RAND_HIG) #第一次抽卡，默认点数大于5000
    click(interval=random())
    
    while True:
        feint_move(GREEN_OK,1,RAND_MID) #确认抽卡
        click(interval=random())
        idle_move(0.5)
        
        while isGacha():
            continue #还没进入开门界面，等待
        
        rand_point = (randint(GREEN_OPEN[0][0],GREEN_OPEN[1][0]),randint(GREEN_OPEN[0][1],GREEN_OPEN[1][1])) #开门
        feint_move(rand_point,0.5,RAND_SUP)
        click(interval=random())
        idle_move(1)
        
        while not isGacha(): #没进入主页面，跳过动画
            rand_point = (randint(GREEN_SKIP[0][0],GREEN_SKIP[1][0]),randint(GREEN_SKIP[0][1],GREEN_SKIP[1][1]))
            feint_move(rand_point,0.5,RAND_SUP)
            click(interval=random())
            idle_move(0.5)
        
        feint_move(GREEN_RESTART,1,RAND_MID) #开始新的一轮
        click(interval=random())
        
        if isZerogreen(): #没绿点了
            return
    
    return
    
#计算抽卡率的函数
def caculator():
    unhook_all() #解绑快捷键，屏蔽按键
    send('backspace') #删除从键盘接收到的数字7
    
    system('cls')
    print("*下面的数据按回车输入，不要带百分号")
    drop_rate=float(input("*请输入指定SSR掉落率（非整体，而是详细页面的单独掉率，单位%）： "))
    trend_ssr=float(input("*请输入流行池中SSR的数量： "))
    stones=float(input("*请输入预计花费的钻石数量，单位为千（如5000输入5，500输入0.5）： "))
    tickets=int(input("*请输入抽卡券数量，10连算10张："))
    
    attemps = int((stones * 2) + tickets) #可以抽的次数
    total_odds = trend_ssr * drop_rate #抽到SSR的概率
    drop_probability = (1-(1-total_odds/100)**attemps)*100 #指定掉落率
    
    print("可抽卡次数: {:.0f}".format(attemps))
    print("单次抽到SSR的概率：{:.2f}%".format(total_odds))
    print("在可抽卡次数内，至少抽到一次指定SSR的概率：{:.2f}%".format(drop_probability))
    input("按回车继续……")
    system('cls') #清屏
    prompt() #重新显示提示
    
    rebound() #重新绑定快捷键
    return
    
#21点算牌的函数，利用高低算牌法
def blackjack():
    unhook_all() #解绑快捷键，屏蔽按键
    send('backspace') #删除从键盘接收到的数字6
    
    system('cls')
    print("*这个算牌辅助工具利用了高低算牌法的技巧")
    print("*请输入当前出现过的所有牌，2~9请输入对应数字再回车")
    print(" 10 J Q K A 请输入字母t再回车")
    print("*一行可以输入一张牌，也可以输入多张牌，用空格隔开")
    print("*程序会根据当前出现的牌判断是继续要牌还是停牌")
    print("*输入r再回车重新开始一场（不是重新发牌，而是退出赌场重进）")
    print("*输入x再回车退出算牌程序")
    
    weight = 0 #权重
    newflag = False
    while True:
        s=input("*请输入出现过的牌：")
        for i in s.split(): #以空格划分割字符串
            if i=='r' or i=='R':
                weight = 0 #权重清零开始新的一场
                print("开始新的一场赌局")
                newflag = True
                break
            elif i=='x' or i=='X':
                system('cls') #清屏
                prompt() #重新显示提示
                rebound() #重新绑定快捷键
                return #回到主菜单
            elif i == '2' or i=='3' or i=='4' or i=='5' or i=='6':
                weight+=1
            elif i== '7' or i=='8' or i=='9':
                pass
            elif i=='t' or i=='T':
                weight-=1
            elif i == ' ':
                pass
            else:
                print("无法识别的牌！请仔细查看说明！或者在主界面按8查看详细帮助！")
        if newflag:
            newflag = False
            continue #新的一局
        if weight>=3:
            print("建议要牌，优势：大")
        elif weight>0:
            print("建议要牌，优势：中")
        elif weight<=0 and weight>-3:
            print("建议停牌，优势：小")
        elif weight<=-3:
            print("建议停牌，优势：极小")
        else:
            print("未知错误！建议重新开始一局！")
    return

#显示详细帮助界面
def helpinfo():
    system('cls')
    send('backspace') #删除从键盘接收到的数字8
    print('DOAXVV挂机防检测版，版本：',VERSION)
    print("帮助说明")
    print("  请先将Auto ON打开，可以在选项里设置自动跳过开启")
    print("  游戏请设置为1080P全屏")
    print("  挂机过程中不要出现弹窗广告、聊天软件挡住屏幕")
    print("  也不要切换窗口或移动鼠标，如要终止请按9")
    print("1.按1重复刷鼠标所在的比赛，体力耗尽为止：")
    print("  进入游戏将鼠标移动到想要重复刷的界面，必须是活动/主要/每日的详细页面")
    print("  不能是推荐页面")
    print("2.按2重复刷鼠标所在的比赛，体力耗尽自动补水：")
    print("  进入游戏将鼠标移动到想要重复刷的界面，必须是活动/主要/每日的详细页面")
    print("  不能是推荐页面")
    print("  体力耗尽后会自动补水，100FP和全满FP都会用")
    print("3.按3重复刷鼠标所在的比赛，自动补水+自动验证（调试中）：")
    print("  进入游戏将鼠标移动到想要重复刷的界面，必须是活动/主要/每日的详细页面")
    print("  不能是推荐页面")
    print("  该功能开发中")
    print("4.按5自动抽绿点，抽完为止：")
    print("  请点开抽绿点的主页面，不要点进去，保证至少有5000以上绿点")
    print("5.按6，21点算牌：")
    print("  使用高低算牌法的技巧，建议仅供参考，只是有更高的概率并非100%赢")
    print("7.按7，计算抽卡概率：")
    print("  确定一定要是单独掉率而非整体掉率，即使是99.99%也不是一定会抽中！")
    print("8.按8显示详细帮助页面")
    print("9.按9结束挂机：")
    print("  会终止当前的任何操作，强制停止程序，当鼠标移动到错误位置时请使用！")
    input("按回车键回到主菜单……")
    prompt()
    return
    
def generate_random_str():
  """
  生成一个随机字符串
  """
  random_str = ''
  base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
  length = len(base_str) - 1
  randomlength=randint(8,16)
  for i in range(randomlength):
    random_str += base_str[randint(0, length)]
  return random_str+".dll"
  
def isAdmin():
    '''判断程序是否有管理员权限'''
    try:
        return windll.shell32.IsUserAnAdmin()
    except:
        return False

#程序启动时的提示，GUI编制完成前的过渡
def prompt():
    system('cls')
    print("DOAXVV挂机防检测版，将Auto ON开启")
    print("版本：",VERSION)
    print("按1重复刷鼠标所在的比赛，体力耗尽为止")
    print("按2重复刷鼠标所在的比赛，体力耗尽自动补水")
    print("按3重复刷鼠标所在的比赛，自动补水+自动验证（调试中）")
    print("按4大跳进行游戏，体力耗尽为止（容易被封）")
    print("按5自动抽绿点，抽完为止")
    print("按6，21点算牌")
    print("按7，计算抽卡概率")
    print("按8显示详细帮助页面")
    print("按9结束挂机")
    print()

#绑定快捷键，call函数
def keybound():
    hook_key('9', stopfarm, suppress=True) #按9结束运行（监听键盘9）
    add_hotkey('1',startfarm,args=(FARM_MODE_1,))  #按1开始不补水运行
    add_hotkey('2',startfarm,args=(FARM_MODE_2,))  #按2开始补水运行
    add_hotkey('3',startfarm,args=(FARM_MODE_3,))  #按3开始补水加验证
    add_hotkey('4',startfarm,args=(FARM_MODE_4,))  #按4大跳进行游戏，体力耗尽为止
    add_hotkey('5',greenpoint) #按5开始抽绿点
    add_hotkey('6',blackjack) #按6开始21点算牌
    add_hotkey('7',caculator) #按7开始计算抽卡概率
    add_hotkey('8',helpinfo) #按8显示帮助界面

    wait()
    return

#重新绑定按键的函数，和keybound的区别在于没有wait()
def rebound():
    hook_key('9', stopfarm, suppress=True) #按9结束运行（监听键盘9）
    add_hotkey('1',startfarm,args=(FARM_MODE_1,))  #按1开始不补水运行
    add_hotkey('2',startfarm,args=(FARM_MODE_2,))  #按2开始补水运行
    add_hotkey('3',startfarm,args=(FARM_MODE_3,))  #按3开始补水加验证
    add_hotkey('4',startfarm,args=(FARM_MODE_4,))  #按4大跳进行游戏，体力耗尽为止
    add_hotkey('5',greenpoint) #按5开始抽绿点
    add_hotkey('6',blackjack) #按6开始21点算牌
    add_hotkey('7',caculator) #按7开始计算抽卡概率
    add_hotkey('8',helpinfo) #按8显示帮助界面

    return
 
#所有主要的操作放在此函数，考虑后续能够针对这个进行进程伪装
def mainproc():
    '''伪装进程的代码'''
    setproctitle(generate_random_str()) #将进程名设为一个随机名字+DLL
    '''gui界面'''
    prompt() #启动提示
    
    keybound() #绑定快捷键
    



#主函数入口
if __name__ == '__main__':
    
    '''
    try:
        if isAdmin(): #有管理员权限
            mainproc() #主进程
        else:
            print("正在自动获取管理员权限")
            windll.shell32.ShellExecuteW(None, "runas", executable, __file__, None, 1) #获取管理员权限
    '''
    mainproc() #主进程，调试用

    '''  
    except FailSafeException:
        print("鼠标移动错误，请勿在程序运行时移动鼠标！")
        print()
    except Exception as e:
        print("未知错误！错误类型")
        print(e)
        print()
    '''  

    _exit(0)
