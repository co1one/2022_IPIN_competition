# ! /usr/bin/env -S python3 -O
# ! /usr/bin/env -S python3

import os
import sys
import lzma
import requests
import time
from parse import parse
import yaml
from evaalapi import statefmt, estfmt
import dataProcessing as dp
sys.path.append('./program')  # 把这个包检索路径添加进去
import main3
import numpy as np

trialsdir = "trials/"
globinifn = "evaalapi.yaml"
# server = "http://127.0.0.1:5000/evaalapi/"
server = "https://evaal.aaloa.org/evaalapi/"
trialname = "S322DYS-BUPT03"
# trialname = "demo"
# S322DYS-BUPT01
# S322DYS-BUPT02
# S322DYS-BUPT03

def do_req(req, n=2):
    r = requests.get(server + trialname + req)
    print("\n==>  GET " + req + " --> " + str(r.status_code))
    if False and r.headers['content-type'].startswith("application/x-xz"):
        l = lzma.decompress(r.content).decode('ascii').splitlines()
    else:
        l = r.text.splitlines()
    if len(l) <= 2 * n + 1:
        print(r.text + '\n')
        # print("成功获取该段数据！！！success！！")
    else:
        print('\n'.join(l[:n]
                        + ["   ... ___%d lines omitted___ ...   " % len(l)]
                        + l[-n:] + [""]))

    return (r)


def input_or_sleep(maxw):
    r = requests.get(server + trialname + "/state")
    s = parse(statefmt, r.text)
    trialts = s['trialts']
    rem = s['rem']
    if trialts > 0:
        print("Trial running, %.3f seconds to timeout" % rem)
    else:
        if trialts == 0:
            print("Trial not started")
        else:  # trialts < 0
            print("Trial timed out %f seconds ago" % -rem)
        rem = 0
    if interactive:
        input("Press Enter to proceed\n")
    else:
        # if rem > 0:
        #     w = min(maxw, max(0, rem - s['S'] / 2))
        # else:
        #     w = maxw
        # print("Waiting for %.1fs...\n" % w)

        w = maxw
        time.sleep(w)


def demo(interactive, maxw):
    ## First of all, reload
    if reloadable:
        print("This is a reloadable trial, so let's start by reloading it to be sure")
        r = do_req("/reload")
        print("对于官方数据，该条指令不会被允许使用\n")

    ## Check initial state
    print("首先，查看数据状态")
    r = do_req("/state")
    s = parse(statefmt, r.text);

    oriPos = s.named['pos'].split(';')  # 初始值列表
    print("初始pos值：", oriPos)
    x_pos = float(oriPos[0])
    y_pos = float(oriPos[1])
    floor_pos = int(oriPos[2])
    print(s.named)

    ## Get first 1s worth of data
    print("---第一个数据---")
    sign = True
    while (sign):
        input_or_sleep(maxw)
        print("找GPS数据......")
        r = do_req("/nextdata?horizon=10")
        data = dp.apiDataProcessing(r.text)
        # 确定第一次
        if (x_pos == 0 and y_pos == 0):
            for row in range(len(data)):
                if (data[row][0] == 'GNSS'):
                    x_pos = float(data[row][4])
                    y_pos = float(data[row][3])
                    sign = False
            print(x_pos, y_pos, floor_pos)




    # Look at remaining time
    input_or_sleep(maxw)
    print("您可以在“nextdata”流中自由混合“state”请求。这对于检查状态可能有用")
    r = do_req("/state")
    print("The return code is the trial state, whose meaning is:")
    s = parse(statefmt, r.text);
    print(s.named)
    print("""'trialts' is 1.0,很正常.'rem' 是剩余时间""")


    ## Set estimates
    input_or_sleep(maxw)
    print("""从现在起，我们不断发送估算数据，并要求提供新的数据......
默认以0.5s为步长。所以我们不设置horizon""")
    while (True):
        # 设置跳出循环的条件
        if (r.status_code != 200 and r.status_code != 423):
            print("数据跑完 or 超时")
            break
        # ------ nextdata ------
        r = do_req("/nextdata?horizon=10&position=%.1f,%.1f,%.1f" % (x_pos, y_pos, floor_pos))
        # here 把main函数加到这里（r.text可以把数据拿出来）
        oriPos = [x_pos, y_pos, floor_pos]
        x_pos, y_pos, floor_pos = main3.main3(r.text, oriPos)  # main函数！！！！
        print(x_pos, y_pos, floor_pos)
        print("********** ************** ************** ***************")

        input_or_sleep(maxw)


    ## Get estimates
    print(
        "获得到目前为止设置的估计列表")
    r = do_req("/estimates", 3)
    print("解析得到的最后一行估计值:")
    s = parse(estfmt, r.text.splitlines()[-1]);
    print(s.named)

    ## Get log
    input_or_sleep(maxw)
    print("您可以获得试用会话的日志，包括所有接收到的数据。同样，这在试验结束时非常有用。")
    r = do_req("/log", 12)

    ## We finish here
    print("Demo stops here")


################################################################

if __name__ == '__main__':

    if len(sys.argv) == 1:
        print("""A demo for the EvAAL API.  Usage is
%s auto|interactive [trial] [server]

if omitted, TRIAL defaults to '%s' and SERVER to %s""" %
              (sys.argv[0], trialname, server))
        exit(1)
    elif sys.argv[1] == 'interactive':
        interactive = True
    elif sys.argv[1] == 'auto':
        interactive = False
    else:
        print("%s -- bad arguments: exiting" % sys.argv[0])
        exit(1)

    if len(sys.argv) > 2:
        trialname = sys.argv[2]

    if len(sys.argv) > 3:
        server = sys.argv[3]

    trialinifn = trialsdir + "demo" + ".yaml"
    if os.path.isfile(trialinifn):
        with open(trialinifn, 'r') as inif:
            ini = yaml.safe_load(inif)
    elif os.path.isfile(globinifn):
        with open(globinifn, 'r') as inif:
            ini = yaml.safe_load(inif)
    else:
        print("%s -- no init file found: exiting" % sys.argv[0])
        exit(2)
    print(ini)
    global reloadable
    reloadable = bool(ini["demo"]['reloadable'])

    print("# Running %s demo test suite\n" % ("interactive" if interactive else "auto"))
    maxw = 10 if trialname == 'slowtest' else 12
    demo(interactive, maxw)
    exit(0)

# Local Variables:
# mode: python
# comment-column: 40
# fill-column: 100
# End:
