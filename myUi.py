# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from kafka import KafkaProducer
import os
import time
import json
import raw_data_handle
import datetime
import requests
import random
import re

base_url = 'https://www.internic.net/domain/root.zone'
with open("./kafka.json") as fp:
    jd = json.load(fp)
kafkaTrans = str(jd['host'])+":"+str(jd['port'])

def sleepTime():        #整五分钟睡眠的剩余秒数
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    nextTime = (datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H")
    minute = (datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime("%M")
    real_minute = int(minute)-int(minute)%5
    time5 = datetime.datetime.strptime(str(nextTime)+":"+str(real_minute)+":00", "%Y-%m-%d %H:%M:%S")
    sec = time5 - datetime.datetime.now()
    return sec.seconds+1

def init_zone_file():       #爬取根文件并获取当前根文件的SOA号
    response = requests.get(base_url)
    s = str(response.text)[0:94]
    ss = s.split()
    with open('rootZoneFile.txt', 'w', encoding='utf-8') as fp:
        fp.write(response.content.decode('utf-8'))
    return ss[6]

def SOA_Serial_Search(filename):        #获取得到的SOA序列号
    with open("raw_data/ipv4/raw_data_"+filename.lower()+".txt", encoding='utf-8') as file:
        data = file.read().split("******")
    flag_udp = re.search(";; ANSWER SECTION:\n[^\n]*", data[2])
    flag_tcp = re.search(";; ANSWER SECTION:\n[^\n]*", data[3])
    if not flag_udp and not flag_tcp:
        return -1
    elif not flag_udp:
        return int(flag_tcp.group().split("\n")[1].split()[6])
    elif not flag_tcp:
        return int(flag_udp.group().split("\n")[1].split()[6])
    SOA_udp = int(flag_udp.group().split("\n")[1].split()[6])
    SOA_tcp = int(flag_tcp.group().split("\n")[1].split()[6])
    return min(SOA_udp, SOA_tcp)

class Ui_Form(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(50, 30, 141, 471))
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)
        self.groupBox.setObjectName("groupBox")
        self.checkBox = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox.setGeometry(QtCore.QRect(30, 60, 91, 19))
        self.checkBox.setObjectName("checkBox")
        self.checkBox_2 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_2.setGeometry(QtCore.QRect(30, 90, 91, 19))
        self.checkBox_2.setObjectName("checkBox_2")
        self.checkBox_3 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_3.setGeometry(QtCore.QRect(30, 120, 91, 19))
        self.checkBox_3.setObjectName("checkBox_3")
        self.checkBox_4 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_4.setGeometry(QtCore.QRect(30, 150, 91, 19))
        self.checkBox_4.setObjectName("checkBox_4")
        self.checkBox_5 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_5.setGeometry(QtCore.QRect(30, 180, 91, 19))
        self.checkBox_5.setObjectName("checkBox_5")
        self.checkBox_6 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_6.setGeometry(QtCore.QRect(30, 210, 91, 19))
        self.checkBox_6.setObjectName("checkBox_6")
        self.checkBox_7 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_7.setGeometry(QtCore.QRect(30, 240, 91, 19))
        self.checkBox_7.setObjectName("checkBox_7")
        self.checkBox_8 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_8.setGeometry(QtCore.QRect(30, 270, 91, 19))
        self.checkBox_8.setObjectName("checkBox_8")
        self.checkBox_9 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_9.setGeometry(QtCore.QRect(30, 300, 91, 19))
        self.checkBox_9.setObjectName("checkBox_9")
        self.checkBox_10 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_10.setGeometry(QtCore.QRect(30, 330, 91, 19))
        self.checkBox_10.setObjectName("checkBox_10")
        self.checkBox_11 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_11.setGeometry(QtCore.QRect(30, 360, 91, 19))
        self.checkBox_11.setObjectName("checkBox_11")
        self.checkBox_12 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_12.setGeometry(QtCore.QRect(30, 390, 91, 19))
        self.checkBox_12.setObjectName("checkBox_12")
        self.checkBox_13 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_13.setGeometry(QtCore.QRect(30, 420, 91, 19))
        self.checkBox_13.setObjectName("checkBox_13")
        self.checkBox_14 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_14.setGeometry(QtCore.QRect(10, 30, 91, 19))
        self.checkBox_14.setTristate(False)
        self.checkBox_14.setObjectName("checkBox_14")
        self.checkBox_14.stateChanged.connect(self.all_select)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(220, 40, 241, 121))
        self.groupBox_2.setFlat(False)
        self.groupBox_2.setCheckable(True)
        self.groupBox_2.setObjectName("groupBox_2")
        self.checkBox_15 = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox_15.setGeometry(QtCore.QRect(30, 30, 91, 19))
        self.checkBox_15.setObjectName("checkBox_15")
        self.checkBox_16 = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox_16.setGeometry(QtCore.QRect(30, 70, 91, 19))
        self.checkBox_16.setObjectName("checkBox_16")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(500, 40, 251, 121))
        self.groupBox_3.setCheckable(True)
        self.groupBox_3.setObjectName("groupBox_3")
        self.checkBox_17 = QtWidgets.QCheckBox(self.groupBox_3)
        self.checkBox_17.setGeometry(QtCore.QRect(30, 30, 91, 19))
        self.checkBox_17.setObjectName("checkBox_17")
        self.checkBox_18 = QtWidgets.QCheckBox(self.groupBox_3)
        self.checkBox_18.setGeometry(QtCore.QRect(30, 70, 91, 19))
        self.checkBox_18.setObjectName("checkBox_18")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(660, 460, 91, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.click)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setGeometry(QtCore.QRect(220, 310, 531, 131))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(220, 270, 531, 31))
        self.textEdit.setObjectName("textEdit")
        self.checkBox_19 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_19.setGeometry(QtCore.QRect(250, 180, 91, 19))
        self.checkBox_19.setObjectName("checkBox_19")
        self.checkBox_20 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_20.setGeometry(QtCore.QRect(250, 220, 91, 19))
        self.checkBox_20.setObjectName("checkBox_20")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindow", "测量根"))
        self.checkBox.setText(_translate("MainWindow", "A"))
        self.checkBox_2.setText(_translate("MainWindow", "B"))
        self.checkBox_3.setText(_translate("MainWindow", "C"))
        self.checkBox_4.setText(_translate("MainWindow", "D"))
        self.checkBox_5.setText(_translate("MainWindow", "E"))
        self.checkBox_6.setText(_translate("MainWindow", "F"))
        self.checkBox_7.setText(_translate("MainWindow", "G"))
        self.checkBox_8.setText(_translate("MainWindow", "H"))
        self.checkBox_9.setText(_translate("MainWindow", "I"))
        self.checkBox_10.setText(_translate("MainWindow", "J"))
        self.checkBox_11.setText(_translate("MainWindow", "K"))
        self.checkBox_12.setText(_translate("MainWindow", "L"))
        self.checkBox_13.setText(_translate("MainWindow", "M"))
        self.checkBox_14.setText(_translate("MainWindow", "全选"))
        self.groupBox_2.setTitle(_translate("MainWindow", "IPv4"))
        self.checkBox_15.setText(_translate("MainWindow", "路由路径"))
        self.checkBox_16.setText(_translate("MainWindow", "参考时延"))
        self.groupBox_3.setTitle(_translate("MainWindow", "IPv6"))
        self.checkBox_17.setText(_translate("MainWindow", "路由路径"))
        self.checkBox_18.setText(_translate("MainWindow", "参考时延"))
        self.pushButton.setText(_translate("MainWindow", "开始监测"))
        self.checkBox_19.setText(_translate("MainWindow", "正确性"))
        self.checkBox_20.setText(_translate("MainWindow", "发布时延"))
        self.checkBox_15.setChecked(True)
        self.checkBox_16.setChecked(True)
        self.checkBox_17.setChecked(True)
        self.checkBox_18.setChecked(True)
        self.checkBox_19.setChecked(True)
        self.checkBox_20.setChecked(True)

    def all_select(self):
        if self.checkBox_14.checkState() == Qt.Checked:
            self.checkBox.setChecked(True)
            self.checkBox_2.setChecked(True)
            self.checkBox_3.setChecked(True)
            self.checkBox_4.setChecked(True)
            self.checkBox_5.setChecked(True)
            self.checkBox_6.setChecked(True)
            self.checkBox_7.setChecked(True)
            self.checkBox_8.setChecked(True)
            self.checkBox_9.setChecked(True)
            self.checkBox_10.setChecked(True)
            self.checkBox_11.setChecked(True)
            self.checkBox_12.setChecked(True)
            self.checkBox_13.setChecked(True)


    def click(self):
        self.plainTextEdit.appendPlainText("系统初始化...")
        QApplication.processEvents()
        old_Serial_num = init_zone_file()   #根文件SOA序列号
        if raw_data_handle.get_database_SOA() != old_Serial_num:
            raw_data_handle.save_root_zone_file()   #保存获取的根文件
        SOA_Latency_count = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]        #记录检测到SOA变化经过几个五分钟
        detect_count = 0        #获取的json# 数据条数
        err_flag = False
        env = ""
        s = ""
        correct = 0
        pub = 0
        if self.checkBox_19.checkState() == Qt.Checked:
            correct = 1
        if self.checkBox_20.checkState() == Qt.Checked:
            pub = 1
        if self.checkBox.checkState() == Qt.Checked:
            env += " a.root-servers.net"
            s += "a"
        if self.checkBox_2.checkState() == Qt.Checked:
            env += " b.root-servers.net"
            s += "b"
        if self.checkBox_3.checkState() == Qt.Checked:
            env += " c.root-servers.net"
            s += "c"
        if self.checkBox_4.checkState() == Qt.Checked:
            env += " d.root-servers.net"
            s += "d"
        if self.checkBox_5.checkState() == Qt.Checked:
            env += " e.root-servers.net"
            s += "e"
        if self.checkBox_6.checkState() == Qt.Checked:
            env += " f.root-servers.net"
            s += "f"
        if self.checkBox_7.checkState() == Qt.Checked:
            env += " g.root-servers.net"
            s += "g"
        if self.checkBox_8.checkState() == Qt.Checked:
            env += " h.root-servers.net"
            s += "h"
        if self.checkBox_9.checkState() == Qt.Checked:
            env += " i.root-servers.net"
            s += "i"
        if self.checkBox_10.checkState() == Qt.Checked:
            env += " j.root-servers.net"
            s += "j"
        if self.checkBox_11.checkState() == Qt.Checked:
            env += " k.root-servers.net"
            s += "k"
        if self.checkBox_12.checkState() == Qt.Checked:
            env += " l.root-servers.net"
            s += "l"
        if self.checkBox_13.checkState() == Qt.Checked:
            env += " m.root-servers.net"
            s += "m"
        if s == "":
            return
        ipv4_command = "./detect_ipv4.sh"
        ipv6_command = "./detect_ipv6.sh"
        if self.groupBox_2.isChecked():
            if self.checkBox_15.checkState() == Qt.Checked:
                ipv4_command += " -t"
            else:
                ipv4_command += " -not"
            if self.checkBox_16.checkState() == Qt.Checked:
                ipv4_command += " -r"
            else:
                ipv4_command += " -nor"
        if self.groupBox_3.isChecked():
            if self.checkBox_17.checkState() == Qt.Checked:
                ipv6_command += " -t"
            else:
                ipv6_command += " -not"
            if self.checkBox_18.checkState() == Qt.Checked:
                ipv6_command += " -r"
            else:
                ipv6_command += " -nor"
        ipv4 = self.groupBox_2.isChecked()
        ipv4_ist = (self.checkBox_15.checkState() == Qt.Checked)
        ipv4_isr = (self.checkBox_16.checkState() == Qt.Checked)
        ipv6 = self.groupBox_3.isChecked()
        ipv6_ist = (self.checkBox_17.checkState() == Qt.Checked)
        ipv6_isr = (self.checkBox_18.checkState() == Qt.Checked)

        init_sleep_time = sleepTime()  # 整五分时间睡眠
        self.plainTextEdit.appendPlainText("睡眠"+str(init_sleep_time)+"秒")
        QApplication.processEvents()
        time.sleep(init_sleep_time)

        while True:
            err_flag = False
            print(datetime.datetime.now())
            print("start")
            bias = random.randint(0, 60)
            self.plainTextEdit.appendPlainText("随机等待时间："+str(bias)+"秒")
            QApplication.processEvents()
            time.sleep(bias)
            self.plainTextEdit.appendPlainText("正在爬取根文件...")
            QApplication.processEvents()
            now_Serial_num = init_zone_file()
            if now_Serial_num != old_Serial_num and pub == 1:  # SOA版本更新
                print("SOA更新")
                raw_data_handle.save_root_zone_file()
                old_Serial_num = now_Serial_num
                for char in s:
                    SOA_Latency_count[ord(char) - ord('a')] += 1
            self.plainTextEdit.appendPlainText("正在监测中...")
            QApplication.processEvents()
            os.system("./detect.sh"+env)
            #print("./detect.sh"+env)
            if self.groupBox_2.isChecked():
                os.system(ipv4_command+env)
                #print(ipv4_command+env)
            if self.groupBox_3.isChecked():
                os.system(ipv6_command+env)
                #print(ipv6_command+env)

            self.plainTextEdit.appendPlainText("正在解析获取到的数据...")
            QApplication.processEvents()
            raw_data_handle.data_init()     #数据初始化为默认值
            if pub == 1:
                for char in s:
                    get_SOA_serial = SOA_Serial_Search(char)
                    if str(get_SOA_serial) != now_Serial_num:
                        if get_SOA_serial != -1 or (get_SOA_serial==-1 and SOA_Latency_count[ord(char) - ord('a')]!=-1):#如果SOA询问未超时且未检测到SOA更新过
                            SOA_Latency_count[ord(char) - ord('a')] += 1
                    else:
                        point = raw_data_handle.data[char.upper()]
                        if SOA_Latency_count[ord(char) - ord('a')] != -1:
                            point['Publication_latency'] = SOA_Latency_count[ord(char) - ord('a')]*5
                        else:
                            point['Publication_latency'] = -1
                        SOA_Latency_count[ord(char) - ord('a')] = -1
                        raw_data_handle.data[char.upper()] = point
            _thread = []
            for root in s:
                thread = raw_data_handle.myThread(root.upper(), "raw_data_"+root+".txt", ipv4, ipv4_ist, ipv4_isr , ipv6, ipv6_ist, ipv6_isr, correct)
                _thread.append(thread)
            for t in _thread:
                t.start()
            for t in _thread:
                t.join()
            for t in _thread:
                if t._error:
                    raw_data_handle.error_record(t.ID)
                    err_flag = True
            if err_flag:
                continue
            #with open("json_data/"+str(raw_data_handle.data['TimeStamp'])+".json", "w") as write_f:
                #write_f.write(json.dumps(raw_data_handle.data, ensure_ascii=False))
            detect_count += 1
            self.textEdit.setPlainText("已获取" + str(detect_count) + "组数据")
            if detect_count%10 == 0:
                self.plainTextEdit.clear()
            '''
            producer = KafkaProducer(bootstrap_servers=[kafkaTrans],
                                     api_version=(0, 10, 0),
                                     value_serializer=lambda v: json.dumps(v).encode('utf-8'))

            future = producer.send("test", raw_data_handle.data, partition=0)
            result = future.get(timeout=10)
            '''
            #print(result)
            raw_data_handle.save()
            self.plainTextEdit.appendPlainText("睡眠...")
            print("end")
            QApplication.processEvents()
            sleep5 = sleepTime()
            time.sleep(sleep5)


