import json
import re
import threading
import pymysql
import random
import string
import os
import ipaddress

json_data = {}
data = json.loads(json.dumps(json_data))
lock = threading.RLock()
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

class myThread(threading.Thread):
    def __init__(self, ID, filename, ipv4, ist_4, isr_4, ipv6, ist_6, isr_6, correct):
        threading.Thread.__init__(self)
        self.ID = ID
        self.filename = filename
        self._error = False
        self.ipv4 = ipv4
        self.ist_4 = ist_4
        self.isr_4 = isr_4
        self.ipv6 = ipv6
        self.ist_6 = ist_6
        self.isr_6 = isr_6
        self.correct = correct

    def run(self):
        basic_handle("./raw_data/"+self.filename, self.ID, self.correct)
        if self.ipv4:
            ipv4_handle("./raw_data/ipv4/"+self.filename, self.ID, self.ist_4, self.isr_4)
        if self.ipv6:
            ipv6_handle("./raw_data/ipv6/"+self.filename, self.ID, self.ist_6, self.isr_6)
        '''
            print("system error")
            self._error = True
        '''


def NS_TLD_verify(filename):    #验证<TLD> NS类型询问结果的正确性
    with open("raw_data/correctness/raw_data_" + filename.lower() + ".txt", encoding='utf-8') as file:
        data = file.read()
    head = re.search("->>HEADER<<-[^\n]+[\n][^\n]+[\n][\n]", str(data))
    if not head:
        return 0
    if "status: NOERROR" not in data:
        return -1
    try:
        if "aa" in head.group():
            return -1
        if "ANSWER: 0" not in head.group():
            return -1
        authority = re.search("AUTHORITY: [0-9]*", head.group())
        author_num = authority.group().split(" ")
        if int(author_num[1]) == 0:
            return -1
        if "RRSIG	DS" not in data and "RRSIG	NSEC" not in data:
            return -1
        if "ADDITIONAL: 1\n" in head.group():
            return -1
    except:
        return -1
    return 1

def DS_TLD_verify(filename):        #验证DS TLD 查询结果的正确性
    with open("raw_data/correctness/raw_data_" + filename.lower() + ".txt", encoding='utf-8') as file:
        data = file.read()
    head = re.search("->>HEADER<<-[^\n]+[\n][^\n]+[\n][\n]", str(data))
    if not head:
        return 0
    if "status: NOERROR" not in data:
        return -1
    try:
        if "aa" not in head.group():
            return -1
        if "ANSWER: 0" in head.group():
            return -1
        if "RRSIG	DS" not in data:
            return -1
        if "ADDITIONAL: 1" not in head.group():
            return -1
        if "AUTHORITY: 0" not in head.group():
            return -1
    except:
        return -1
    return 1


def dot_SOA_verify(filename):       #验证SOA . 查询结果的正确性
    with open("raw_data/correctness/raw_data_" + filename.lower() + ".txt", encoding='utf-8') as file:
        data = file.read()
    head = re.search("->>HEADER<<-[^\n]+[\n][^\n]+[\n][\n]", str(data))
    if not head:
        return 0
    if "status: NOERROR" not in data:
        return -1
    try:
        if "aa" not in head.group():
            return -1
        if "ANSWER: 0" in head.group():
            return -1
        if "RRSIG	SOA" not in data:
            return -1
        if "RRSIG	NS" not in data:
            return -1
        if "AUTHORITY: 0" in head.group():
            return -1
    except:
        return -1
    return 1

def dot_NS_verify(filename):        #验证NS . 查询结果的正确性
    with open("raw_data/correctness/raw_data_" + filename.lower() + ".txt", encoding='utf-8') as file:
        data = file.read()
    head = re.search("->>HEADER<<-[^\n]+[\n][^\n]+[\n][\n]", str(data))
    if not head:
        return 0
    if "status: NOERROR" not in data:
        return -1
    try:
        if "aa" not in head.group():
            return -1
        if "ANSWER: 0" in head.group():
            return -1
        if "RRSIG	NS" not in data:
            return -1
        if "AUTHORITY: 0" not in head.group():
            return -1
    except:
        return -1
    return 1

def dot_DNSKEY_verify(filename):        #验证DNSKEY . 查询的正确性
    with open("raw_data/correctness/raw_data_" + filename.lower() + ".txt", encoding='utf-8') as file:
        data = file.read()
    head = re.search("->>HEADER<<-[^\n]+[\n][^\n]+[\n][\n]", str(data))
    if not head:
        return 0
    if "status: NOERROR" not in data:
        return -1
    try:
        if "aa" not in head.group():
            return -1
        if "ANSWER: 0" in head.group():
            return -1
        if "RRSIG	DNSKEY" not in data:
            return -1
        if "AUTHORITY: 0" not in head.group():
            return -1
        if "ADDITIONAL: 1" not in head.group():
            return -1
    except:
        return -1
    return 1

def neg_verify(filename):       #验证negative询问的正确性
    with open("raw_data/correctness/raw_data_" + filename.lower() + ".txt", encoding='utf-8') as file:
        data = file.read()
    head = re.search("->>HEADER<<-[^\n]+[\n][^\n]+[\n][\n]", str(data))
    if not head:
        return 0
    if "status: NXDOMAIN" not in data:
        return -1
    try:
        if "aa" not in head.group():
            return -1
        if "ANSWER: 0" not in head.group():
            return -1
        if "RRSIG	NSEC" not in data:
            return -1
        if "RRSIG	SOA" not in data:
            return -1
        if "AUTHORITY: 0" in head.group():
            return -1
        if "ADDITIONAL: 1" not in head.group():
            return -1
    except:
        return -1
    return 1

def correct_shell():
    pos_or_neg = random.randint(0,10)
    if pos_or_neg == 0:
        return "www.rssac047-test." + "".join(random.choice(string.ascii_letters) for i in range(10))+" A +dnssec +norecurse", 5
    else:
        type = random.randint(0,5)
        if type == 0:
            lock.acquire()
            conn.ping(reconnect=True)
            cur = conn.cursor()
            sql = "select distinct name from root_data where type='NS' and name!='.' order by rand() limit 0,1"
            cur.execute(sql)
            data = cur.fetchone()
            lock.release()
            return data[0]+" NS +dnssec +norecurse", 0
        elif type == 1:
            lock.acquire()
            conn.ping(reconnect=True)
            cur = conn.cursor()
            sql = "select distinct name from root_data where type='DS' order by rand() limit 0,1"
            cur.execute(sql)
            data = cur.fetchone()
            lock.release()
            return data[0] + " DS +dnssec +norecurse", 1
        elif type == 2:
            return  ". SOA +dnssec +norecurse", 2
        elif type == 3:
            return  ". NS +dnssec +norecurse", 3
        else:
            return ". DNSKEY +dnssec +norecurse", 4

def basic_handle(filename, ID, correct):
    f = open(filename, "r", encoding='utf-8')
    tmp = str(f.readlines()).replace("\\n', '", "").split("******")
    data['TimeStamp'] = tmp[1]
    _root = data[ID]
    try:
        _root['Identification'] = tmp[2].split("\"")[1]
    except:
        _root['Identification'] = ""
    status = re.search('status: [A-Z]*', tmp[3])
    try:
        _root['Status'] = status.group().split(" ")[1]
    except:
        _root['Status'] = ""
        
    if correct == 1:
        shell , type = correct_shell()
        correct_sh = "dig @"+ID.lower()+".root-servers.net "+shell+" +tcp > ./raw_data/correctness/raw_data_"+ID.lower()+".txt"
        os.system(correct_sh)
        # 验证正确性
        if type == 0:
            _root['Correctness'] = NS_TLD_verify(ID)
        elif type == 1:
            _root['Correctness'] = DS_TLD_verify(ID)
        elif type == 2:
            _root['Correctness'] = dot_SOA_verify(ID)
        elif type == 3:
            _root['Correctness'] = dot_NS_verify(ID)
        elif type == 4:
            _root['Correctness'] = dot_DNSKEY_verify(ID)
        else:
            _root['Correctness'] = neg_verify(ID)
        if _root['Correctness'] == -1:
            print(type)

    data[ID] = _root

def ipv4_handle(filename, ID, ist, isr):
    f = open(filename, "r", encoding='utf-8')
    tmp = str(f.readlines()).replace("\\n', '", "\n").split("******")
    point = data[ID]
    pub_ip = re.search('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', tmp[1])

    if pub_ip:
        point['SourceIP_ipv4'] = pub_ip.group()

    query_latency = point['QueryLatency']
    query_ipv4 = re.search('Query time: [0-9]+', tmp[2])
    if query_ipv4:
        query_latency['Ipv4_udp'] = query_ipv4.group().split(" ")[2]
    else:
        query_latency['Ipv4_udp'] = 4000
    query_ipv4 = re.search('Query time: [0-9]+', tmp[3])
    if query_ipv4:
        query_latency['Ipv4_tcp'] = query_ipv4.group().split(" ")[2]
    else:
        query_latency['Ipv4_tcp'] = 4000
    point['QueryLatency'] = query_latency

    if ist:
        trace = tmp[4].split("\n")
        i = 2
        point['Path_count_ipv4'] = len(trace) - 3
        _route = json.loads(json.dumps(json_data))
        while i < len(trace) - 1:
            route = re.search('[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*', trace[i])
            if route:
                _route['Router' + str(i - 2)] = route.group()
            else:
                _route['Router' + str(i - 2)] = "* * *"
            i += 1
        point['Path_ipv4'] = _route

    bias = 0
    if ist:
        bias += 1
    if isr:
        refer_latency = point['ReferLatency_ipv4']
        ref = re.search('Query time: [0-9]+', tmp[4+bias])
        if ref:
            refer_latency['AliDNS'] = ref.group().split(" ")[2]
        else:
            refer_latency['AliDNS'] = 4000
        ref = re.search('Query time: [0-9]+', tmp[5 + bias])
        if ref:
            refer_latency['114DNS'] = ref.group().split(" ")[2]
        else:
            refer_latency['114DNS'] = 4000
        ref = re.search('Query time: [0-9]+', tmp[6 + bias])
        if ref:
            refer_latency['DNSPod'] = ref.group().split(" ")[2]
        else:
            refer_latency['DNSPod'] = 4000
        point['ReferLatency_ipv4'] = refer_latency

    data[ID] = point


def ipv6_handle(filename, ID, ist, isr):
    f = open(filename, "r", encoding='utf-8')
    tmp = str(f.readlines()).replace("\\n', '", "\n").split("******")
    point = data[ID]
    pub_ip = re.search('^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))', tmp[1].replace("\"", ""))

    if pub_ip:
        point['SourceIP_ipv6'] = str(pub_ip.group()).replace("\n","")

    query_latency = point['QueryLatency']
    query_ipv4 = re.search('Query time: [0-9]+', tmp[2])
    if query_ipv4:
        query_latency['Ipv6_udp'] = query_ipv4.group().split(" ")[2]
    else:
        query_latency['Ipv6_udp'] = 4000
    query_ipv4 = re.search('Query time: [0-9]+', tmp[3])
    if query_ipv4:
        query_latency['Ipv6_tcp'] = query_ipv4.group().split(" ")[2]
    else:
        query_latency['Ipv6_tcp'] = 4000
    point['QueryLatency'] = query_latency

    if ist:
        trace = tmp[4].split("\n")
        i = 2
        point['Path_count_ipv6'] = len(trace) - 3
        _route = json.loads(json.dumps(json_data))
        while i < len(trace) - 1:
            route = re.search("((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)(\\.(25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)(\\.(25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)(\\.(25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)(\\.(25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)(\\.(25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)(\\.(25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)(\\.(25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)){3}))|:)))(%.+)?", trace[i])

            if route:
                _route['Router' + str(i - 2)] = str(route.group()).replace("\n","")
            else:
                _route['Router' + str(i - 2)] = "* * *"
            i += 1
        point['Path_ipv6'] = _route

    bias = 0
    if ist:
        bias += 1
    if isr:
        refer_latency = point['ReferLatency_ipv6']
        ref = re.search('Query time: [0-9]+', tmp[4 + bias])
        if ref:
            refer_latency['AliDNS'] = ref.group().split(" ")[2]
        else:
            refer_latency['AliDNS'] = 4000
        ref = re.search('Query time: [0-9]+', tmp[5 + bias])
        if ref:
            refer_latency['114DNS'] = ref.group().split(" ")[2]
        else:
            refer_latency['114DNS'] = 4000
        ref = re.search('Query time: [0-9]+', tmp[6 + bias])
        if ref:
            refer_latency['DNSPod'] = ref.group().split(" ")[2]
        else:
            refer_latency['DNSPod'] = 4000
        point['ReferLatency_ipv6'] = refer_latency

    data[ID] = point


def save():
    conn.ping(reconnect=True)
    cur = conn.cursor()
    sql = "INSERT INTO `log` VALUES ('"+str(data['TimeStamp'])+"','"+json.dumps(data['A'])+"','"+json.dumps(data['B'])+"','"+json.dumps(data['C'])\
          +"','"+json.dumps(data['D'])+"','"+json.dumps(data['E'])+"','"+json.dumps(data['F'])+"','"+json.dumps(data['G'])+"','"+json.dumps(data['H'])\
          +"','"+json.dumps(data['I'])+"','"+json.dumps(data['J'])+"','"+json.dumps(data['K'])+"','"+json.dumps(data['L'])+"','"+json.dumps(data['M'])+"')"
    #print(sql)
    cur.execute(sql)
    conn.commit()
    conn.close()

def error_record(ID):
    file1 = open('./raw_data/raw_data_'+ID.lower()+'.txt', "r", encoding='utf-8')
    file2 = open("./error_log/"+str(data['TimeStamp']).replace(":","-")+"_"+ID+".txt", "w", encoding='utf-8')
    s = file1.read()
    file2.write(s)

def save_root_zone_file():      #将根文件存入数据库
    with open("rootZoneFile.txt") as file:
        line = file.readline()
        conn.ping(reconnect=True)
        cur = conn.cursor()
        sql = "delete from root_data"
        cur.execute(sql)
        conn.commit()
        sql = "delete from root_data2"
        cur.execute(sql)
        conn.commit()
        while line:
            RR_list = line.split()
            if RR_list[3] == "NS" or RR_list[3] == "A" or RR_list[3] == "AAAA" or RR_list[3] == "SOA" or RR_list[3] == "DS":
                s = RR_list[4]
                for i in range(5, len(RR_list)):
                    s = s + " " + RR_list[i]
                sql = "insert into root_data values('"+RR_list[0]+"','"+RR_list[1]+"','"+RR_list[2]+"','"+RR_list[3]+"','"+s+"')"
                # print(sql)
                cur.execute(sql)
                conn.commit()
            elif RR_list[3] == "RRSIG":
                s = RR_list[5]
                for i in range(6, len(RR_list)):
                    s = s + " " + RR_list[i]
                sql = "insert into root_data2 values('" + RR_list[0] + "','" + RR_list[1] + "','" + RR_list[2] + "','" + \
                      RR_list[3] + "','" + RR_list[4] + "','" + s + "')"
                cur.execute(sql)
                conn.commit()
            elif RR_list[3] == "DNSKEY":
                s = RR_list[4]
                for i in range(5, len(RR_list)):
                    s = s + " " + RR_list[i]
                sql = "insert into root_data2 values('" + RR_list[0] + "','" + RR_list[1] + "','" + RR_list[2] + "','" + \
                      RR_list[3] + "', null ,'" + s + "')"
                cur.execute(sql)
                conn.commit()
            line = file.readline()

def get_database_SOA():
    conn.ping(reconnect=True)
    cur = conn.cursor()
    sql = "select data from root_data where type = 'SOA' and name = '.'"
    cur.execute(sql)
    try:
        result = cur.fetchone()[0].split()[2]
        return result
    except:
        return ""

#数据初始化为默认值
def data_init():
    for c in 'ABCDEFGHIJKLM':
        point = json.loads(json.dumps(json_data))
        point['Identification'] = ""
        point['Correctness'] = 0
        query_lantancy = json.loads(json.dumps(json_data))
        query_lantancy['Ipv4_udp'] = -1
        query_lantancy['Ipv4_tcp'] = -1
        query_lantancy['Ipv6_udp'] = -1
        query_lantancy['Ipv6_tcp'] = -1
        point['QueryLatency'] = query_lantancy
        point['Path_count_ipv4'] = -1
        point['Path_ipv4'] = ""
        point['Path_count_ipv6'] = -1
        point['Path_ipv6'] = ""
        ReferLatency_ipv4 = json.loads(json.dumps(json_data))
        ReferLatency_ipv4['AliDNS'] = -1
        ReferLatency_ipv4['114DNS'] = -1
        ReferLatency_ipv4['DNSPod'] = -1
        point['ReferLatency_ipv4'] = ReferLatency_ipv4
        ReferLatency_ipv6 = json.loads(json.dumps(json_data))
        ReferLatency_ipv6['AliDNS'] = -1
        ReferLatency_ipv6['114DNS'] = -1
        ReferLatency_ipv6['DNSPod'] = -1
        point['ReferLatency_ipv6'] = ReferLatency_ipv6
        point['Status'] = ""
        point['SourceIP_ipv4'] = ""
        point['SourceIP_ipv6'] = ""
        point['Publication_latency'] = -1
        data[c] = point




