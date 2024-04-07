#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
Program:        DOAXVV AutoFarm
Version:        0.8.3
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
Date: 2022.4.25
Author: Chaobs
Update Log:
2022.4.25： 全部代码用OOP重写，鼠标操作封装到类中
            返回主菜单功能依然没有实现，OCR识别验证码依然没有测试
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


class Version():
    '''
    这个类定义当前程序的版本
    '''
    #程序版本
    version = 'v0.8.3'

    @classmethod
    def tell_version(cls):
        return cls.version

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

class ScreenPlace():
    '''
    这个类储存屏幕上各个点，用来进行识色或点击
    '''
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