import pymysql
import json
import matplotlib.pyplot as plt
import pandas as pd
import math
import platform

with open("./database.json") as fp:
    jd = json.load(fp)
conn = pymysql.connect(
        host = jd["host"],
        port = jd["port"],
        user = jd["user"],
        passwd = jd["passwd"],
        db = jd["db"],
        charset = jd["charset"],
    )

sys_info = str(platform.uname()).replace("uname_result", "").replace("(", "").replace(")", "").replace("=",":")

def refer_perform(performance):#根据阈值设置performance
    refer = []
    flag = []
    for i in range(0,4):
        if performance[i]<96:
            refer.append("< 96%")
            flag.append(0)
        else:
            refer.append(">= 96%")
            flag.append(1)
    for i in range(0, 2):
        if performance[4+i*2]<250:
            refer.append("<= 250ms")
            flag.append(1)
        else:
            refer.append("> 250ms")
            flag.append(0)
        if performance[5+i*2]<500:
            refer.append("<= 500ms")
            flag.append(1)
        else:
            refer.append("> 500ms")
            flag.append(0)
    if performance[8]<70:
        refer.append("<= 70%")
        flag.append(0)
    else:
        refer.append("> 70%")
        flag.append(1)
    if performance[9]<65:
        refer.append("<= 65min")
        flag.append(1)
    else:
        refer.append("> 65min")
        flag.append(0)
    return refer,flag

def statistic_RSI():
    for RSI in 'ABCDEFGHIJKLM':
        measurements = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ipv4_tcp = []
        ipv4_udp = []
        ipv6_tcp = []
        ipv6_udp = []
        ipv4_tcp_del = []
        ipv4_udp_del = []
        ipv6_tcp_del = []
        ipv6_udp_del = []
        publication_lantancy = []
        ipv4_tcp_timeout = 0
        ipv4_udp_timeout = 0
        ipv6_tcp_timeout = 0
        ipv6_udp_timeout = 0
        correct_num = 0
        correct_num_total = 0
        cur = conn.cursor()
        sql = "select " + RSI + " from log"
        cur.execute(sql)
        result = cur.fetchone()
        while result:
            data = json.loads(result[0])
            ipv4_tcp.append(int(data['QueryLatency']['Ipv4_tcp']))
            ipv4_udp.append(int(data['QueryLatency']['Ipv4_udp']))
            ipv6_tcp.append(int(data['QueryLatency']['Ipv6_tcp']))
            ipv6_udp.append(int(data['QueryLatency']['Ipv6_udp']))
            publication_lantancy.append(int(data['Publication_latency']))
            if int(data['Correctness']) == 0:
                result = cur.fetchone()
                continue
            if int(data['Correctness']) == 1:
                correct_num = correct_num+1
            correct_num_total = correct_num_total +1
            result = cur.fetchone()
        for i in range(0,len(ipv4_tcp)):
            if ipv4_tcp[i]>=4000:
                ipv4_tcp_timeout = ipv4_tcp_timeout+1
                ipv4_tcp_del.append(ipv4_tcp[i])
        for i in range(0,len(ipv4_udp)):
            if ipv4_udp[i]>=4000:
                ipv4_udp_timeout = ipv4_udp_timeout+1
                ipv4_udp_del.append(ipv4_udp[i])
        for i in range(0,len(ipv6_tcp)):
            if ipv6_tcp[i]>=4000:
                ipv6_tcp_timeout = ipv6_tcp_timeout+1
                ipv6_tcp_del.append(ipv6_tcp[i])
        for i in range(0,len(ipv6_udp)):
            if ipv6_udp[i]>=4000:
                ipv6_udp_timeout = ipv6_udp_timeout+1
                ipv6_udp_del.append(ipv6_udp[i])
        #移除值为-1的元素，-1代表未检测
        count = ipv4_udp.count(-1)
        for i in range(0, count):
            ipv4_udp.remove(-1)
        count = ipv4_tcp.count(-1)
        for i in range(0, count):
            ipv4_tcp.remove(-1)
        count = ipv6_udp.count(-1)
        for i in range(0, count):
            ipv6_udp.remove(-1)
        count = ipv6_tcp.count(-1)
        for i in range(0, count):
            ipv6_tcp.remove(-1)
        #移除超时元素
        for i in ipv4_tcp_del:
            ipv4_tcp.remove(i)
        for i in ipv4_udp_del:
            ipv4_udp.remove(i)
        for i in ipv6_tcp_del:
            ipv6_tcp.remove(i)
        for i in ipv6_udp_del:
            ipv6_udp.remove(i)
        count = publication_lantancy.count(-1)
        for i in range(0, count):
            publication_lantancy.remove(-1)
        if len(publication_lantancy)==0:
            publication_time = -1
        else:
            publication_lantancy.sort()
            publication_time = publication_lantancy[int(len(publication_lantancy)/2)]
        ipv4_tcp.sort()
        ipv4_udp.sort()
        ipv6_tcp.sort()
        ipv6_udp.sort()
        performance = [int(len(ipv4_udp) / (len(ipv4_udp) + ipv4_udp_timeout)*100), int(len(ipv4_tcp)/(len(ipv4_tcp)+ipv4_tcp_timeout)*100),
                      int(len(ipv6_udp) / (len(ipv6_udp) + ipv6_udp_timeout)*100), int(len(ipv6_tcp) / (len(ipv6_tcp) + ipv6_tcp_timeout)*100),
                        ipv4_udp[int(len(ipv4_udp) / 2)], ipv4_tcp[int(len(ipv4_tcp)/2)], ipv6_udp[int(len(ipv6_udp) / 2)], ipv6_tcp[int(len(ipv6_tcp) / 2)],
                       int(correct_num/correct_num_total*100), publication_time]

        measurements[0] = len(ipv4_udp) + ipv4_udp_timeout
        measurements[1] = len(ipv4_tcp) + ipv4_tcp_timeout
        measurements[2] = len(ipv6_udp) + ipv6_udp_timeout
        measurements[3] = len(ipv6_tcp) + ipv6_tcp_timeout
        measurements[4] = len(ipv4_udp)
        measurements[5] = len(ipv4_tcp)
        measurements[6] = len(ipv6_udp)
        measurements[7] = len(ipv6_tcp)
        measurements[8] = correct_num_total
        measurements[9] = len(publication_lantancy)
        print(RSI+"根ipv4_tcp可用性：",len(ipv4_tcp)/(len(ipv4_tcp)+ipv4_tcp_timeout))
        print(RSI+"根ipv4_tcp时延",ipv4_tcp[int(len(ipv4_tcp)/2)])
        print(RSI+"根ipv4_udp可用性：", len(ipv4_udp) / (len(ipv4_udp) + ipv4_udp_timeout))
        print(RSI+"根ipv4_udp时延", ipv4_udp[int(len(ipv4_udp) / 2)])
        print(RSI+"根ipv6_tcp可用性：", len(ipv6_tcp) / (len(ipv6_tcp) + ipv6_tcp_timeout))
        print(RSI+"根ipv6_tcp时延", ipv6_tcp[int(len(ipv6_tcp) / 2)])
        print(RSI+"根ipv6_udp可用性：", len(ipv6_udp) / (len(ipv6_udp) + ipv6_udp_timeout))
        print(RSI+"根ipv6_udp时延", ipv6_udp[int(len(ipv6_udp) / 2)])
        print(RSI+"根正确性：",correct_num/correct_num_total)
        print(RSI+"根发布时延：", publication_time)

        refer , flag = refer_perform(performance)
        draw_RSI(RSI, refer, measurements , flag)


def draw_RSI(RSI, performance, measurements, flag):
    root = []
    metric = ["IPv4 UDP Availability", "IPv4 TCP Availability", "IPv6 UDP Availability", "IPv6 TCP Availability",
              "IPv4 UDP Latency", "IPv4 TCP Latency", "IPv6 UDP Latency", "IPv6 TCP Latency", "Correctness", "Publication Latency"]
    for i in range(0, 10):
        root.append(RSI+"-Root")
    data = {
        'RSI': root,
        'metric': metric,
        'Performance' : performance,
        'Measurements' : measurements,
    }

    df = pd.DataFrame(data)

    fig, ax = plt.subplots(figsize=(10, 10))

    ax.axis('off')
    ax.axis('tight')

    tb = ax.table(cellText=df.values,
                  colLabels=df.columns,
                  bbox=[0, 0, 1, 1],
                  loc='center',
                  rowLoc='center',
                  cellLoc='center'
                  )

    tb[0, 0].set_facecolor('#363636')
    tb[0, 1].set_facecolor('#363636')
    tb[0, 2].set_facecolor('#363636')
    tb[0, 3].set_facecolor('#363636')
    tb[0, 0].set_text_props(color='w')
    tb[0, 1].set_text_props(color='w')
    tb[0, 2].set_text_props(color='w')
    tb[0, 3].set_text_props(color='w')
    for i in range(0,10):
        if flag[i]:
            tb[i+1, 2].set_facecolor('#00FF00')
        else:
            tb[i + 1, 2].set_facecolor('#FF0000')
    plt.title(sys_info, fontsize='small')
    plt.savefig("report/"+RSI+"-report.png")


def statistic_RSS():
    measurements = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ipv4_udp_total = 0
    ipv4_tcp_total = 0
    ipv6_udp_total = 0
    ipv6_tcp_total = 0
    ipv4_udp_count = 0
    ipv4_tcp_count = 0
    ipv6_udp_count = 0
    ipv6_tcp_count = 0
    ipv4_udp_latency = []
    ipv4_tcp_latency = []
    ipv6_udp_latency = []
    ipv6_tcp_latency = []
    correct_num = 0
    publication_latency = []
    cur = conn.cursor()
    sql = "select * from log"
    cur.execute(sql)
    result = cur.fetchone()
    while result:
        ipv4_udp_k = 0
        ipv4_tcp_k = 0
        ipv6_udp_k = 0
        ipv6_tcp_k = 0
        ipv4_udp_pass = 0
        ipv4_tcp_pass = 0
        ipv6_udp_pass = 0
        ipv6_tcp_pass = 0
        ipv4_udp_min_latency = 40000
        ipv4_tcp_min_latency = 40000
        ipv6_udp_min_latency = 40000
        ipv6_tcp_min_latency = 40000
        for i in range(1,len(result)):
            data = json.loads(result[i])
            if int(data['QueryLatency']['Ipv4_udp']) != -1:
                if int(data['QueryLatency']['Ipv4_udp']) < ipv4_udp_min_latency:
                    ipv4_udp_min_latency = int(data['QueryLatency']['Ipv4_udp'])
                measurements[0] = measurements[0]+1
                measurements[4] = measurements[4]+1
                ipv4_udp_k = ipv4_udp_k+1
                if int(data['QueryLatency']['Ipv4_udp']) < 4000:
                    ipv4_udp_pass = ipv4_udp_pass + 1
            if int(data['QueryLatency']['Ipv4_tcp']) != -1:
                if int(data['QueryLatency']['Ipv4_tcp']) < ipv4_tcp_min_latency:
                    ipv4_tcp_min_latency = int(data['QueryLatency']['Ipv4_tcp'])
                measurements[1] = measurements[1] +1
                measurements[5] = measurements[5]+1
                ipv4_tcp_k = ipv4_tcp_k+1
                if int(data['QueryLatency']['Ipv4_tcp']) < 4000:
                    ipv4_tcp_pass = ipv4_tcp_pass + 1
            if int(data['QueryLatency']['Ipv6_udp']) != -1:
                if int(data['QueryLatency']['Ipv6_udp']) < ipv6_udp_min_latency:
                    ipv6_udp_min_latency = int(data['QueryLatency']['Ipv6_udp'])
                measurements[2] = measurements[2] + 1
                measurements[6] = measurements[6] + 1
                ipv6_udp_k = ipv6_udp_k+1
                if int(data['QueryLatency']['Ipv6_udp']) < 4000:
                    ipv6_udp_pass = ipv6_udp_pass + 1
            if int(data['QueryLatency']['Ipv6_tcp']) != -1:
                if int(data['QueryLatency']['Ipv6_tcp']) < ipv6_tcp_min_latency:
                    ipv6_tcp_min_latency = int(data['QueryLatency']['Ipv6_tcp'])
                measurements[3] = measurements[3] + 1
                measurements[7] = measurements[7] + 1
                ipv6_tcp_k = ipv6_tcp_k+1
                if int(data['QueryLatency']['Ipv6_tcp']) < 4000:
                    ipv6_tcp_pass = ipv6_tcp_pass + 1
            if int(data['Correctness']) != 0:
                measurements[8] = measurements[8] + 1
                if int(data['Correctness']) == 1:
                    correct_num  = correct_num + 1
            if int(data['Publication_latency']) != -1:
                measurements[9] = measurements[9] + 1
                publication_latency.append(int(data['Publication_latency']))
        if ipv4_udp_min_latency != 40000:
            ipv4_udp_latency.append(ipv4_udp_min_latency)
        if ipv4_tcp_min_latency != 40000:
            ipv4_tcp_latency.append(ipv4_tcp_min_latency)
        if ipv6_udp_min_latency != 40000:
            ipv6_udp_latency.append(ipv6_udp_min_latency)
        if ipv6_tcp_min_latency != 40000:
            ipv6_tcp_latency.append(ipv6_tcp_min_latency)
        ipv4_udp_K = math.ceil(2 / 3 * (ipv4_udp_k - 1))
        ipv4_tcp_K = math.ceil(2 / 3 * (ipv4_tcp_k - 1))
        ipv6_udp_K = math.ceil(2 / 3 * (ipv6_udp_k - 1))
        ipv6_tcp_K = math.ceil(2 / 3 * (ipv6_tcp_k - 1))
        ipv4_udp_total = ipv4_udp_total + ipv4_udp_K
        ipv4_tcp_total = ipv4_tcp_total + ipv4_tcp_K
        ipv6_udp_total = ipv6_udp_total + ipv6_udp_K
        ipv6_tcp_total = ipv6_tcp_total + ipv6_tcp_K
        ipv4_udp_count = ipv4_udp_count + min(ipv4_udp_pass, ipv4_udp_K)
        ipv4_tcp_count = ipv4_tcp_count + min(ipv4_tcp_pass, ipv4_tcp_K)
        ipv6_udp_count = ipv6_udp_count + min(ipv6_udp_pass, ipv6_udp_K)
        ipv6_tcp_count = ipv6_tcp_count + min(ipv6_tcp_pass, ipv6_tcp_K)

        result = cur.fetchone()
    ipv4_udp_latency.sort()
    ipv4_tcp_latency.sort()
    ipv6_udp_latency.sort()
    ipv6_tcp_latency.sort()

    print("RSS ipv4_udp可用性：", ipv4_udp_count / ipv4_udp_total)
    print("RSS ipv4_tcp可用性：", ipv4_tcp_count / ipv4_tcp_total)
    print("RSS ipv6_udp可用性：", ipv6_udp_count / ipv6_udp_total)
    print("RSS ipv6_tcp可用性：", ipv6_tcp_count / ipv6_tcp_total)
    print("RSS ipv4_udp时延：", ipv4_udp_latency[int(len(ipv4_udp_latency)/2)])
    print("RSS ipv4_tcp时延：", ipv4_tcp_latency[int(len(ipv4_tcp_latency)/2)])
    print("RSS ipv6_udp时延：", ipv6_udp_latency[int(len(ipv6_udp_latency)/2)])
    print("RSS ipv6_tcp时延：", ipv6_tcp_latency[int(len(ipv6_tcp_latency)/2)])
    print("RSS 正确性：", correct_num/measurements[8])
    if measurements[9] == 0:
        print("RSS 发布时延：-1")
    else:
        print("RSS 发布时延：", publication_latency[int(len(publication_latency)/2)])
    if measurements[9] == 0:
        pub = -1
    else:
        pub = publication_latency[int(len(publication_latency)/2)]
    performance = [int(ipv4_udp_count / ipv4_udp_total*100), int(ipv4_tcp_count / ipv4_tcp_total*100), int(ipv6_udp_count / ipv6_udp_total*100),
                   int(ipv6_tcp_count / ipv6_tcp_total*100), ipv4_udp_latency[int(len(ipv4_udp_latency)/2)], ipv4_tcp_latency[int(len(ipv4_tcp_latency)/2)],
                   ipv6_udp_latency[int(len(ipv6_udp_latency)/2)], ipv6_tcp_latency[int(len(ipv6_tcp_latency)/2)], int(correct_num/measurements[8]*100),
                   pub]
    flag = []
    for i in range(0, 4):
        if performance[i] < 99:
            flag.append(0)
        else:
            flag.append(1)
    for i in range(0, 2):
        if performance[4 + i*2] <=150:
            flag.append(1)
        else:
            flag.append(0)
        if performance[5 + i*2] <=300:
            flag.append(1)
        else:
            flag.append(0)
    if performance[8] < 95 :
        flag.append(0)
    else:
        flag.append(1)
    if performance[9] > 35:
        flag.append(0)
    else:
        flag.append(1)
    draw_RSS(performance, measurements, flag)


def draw_RSS(performance, measurements, flag):
    root = []
    metric = ["IPv4 UDP Availability", "IPv4 TCP Availability", "IPv6 UDP Availability", "IPv6 TCP Availability",
              "IPv4 UDP Latency", "IPv4 TCP Latency", "IPv6 UDP Latency", "IPv6 TCP Latency", "Correctness",
              "Publication Latency"]
    for i in range(0, 10):
        root.append("RSS")
    for i in range(0, 4):
        performance[i] = str(performance[i]) + "%"
    for i in range(4, 8):
        performance[i] = str(performance[i]) + "ms"
    performance[8] = str(performance[8]) + "%"
    performance[9] = str(performance[9]) + "min"
    data = {
        'RSI': root,
        'metric': metric,
        'Performance': performance,
        'Measurements': measurements,
    }

    df = pd.DataFrame(data)

    fig, ax = plt.subplots(figsize=(10, 10))

    ax.axis('off')
    ax.axis('tight')

    tb = ax.table(cellText=df.values,
                  colLabels=df.columns,
                  bbox=[0, 0, 1, 1],
                  loc='center',
                  rowLoc='center',
                  cellLoc='center'
                  )

    tb[0, 0].set_facecolor('#363636')
    tb[0, 1].set_facecolor('#363636')
    tb[0, 2].set_facecolor('#363636')
    tb[0, 3].set_facecolor('#363636')
    tb[0, 0].set_text_props(color='w')
    tb[0, 1].set_text_props(color='w')
    tb[0, 2].set_text_props(color='w')
    tb[0, 3].set_text_props(color='w')
    for i in range(0, 10):
        if flag[i]:
            tb[i + 1, 2].set_facecolor('#00FF00')
        else:
            tb[i + 1, 2].set_facecolor('#FF0000')
    plt.title(sys_info, fontsize='small')
    plt.savefig("report/RSS-report.png")



