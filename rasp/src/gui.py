# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './src/gui.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from utils.models import DatabaseManager
from utils.prints import console
from bleak import BleakScanner
import asyncio
import time
import threading
import struct
from ble.main_client import BleClient
from utils.models import DatabaseManager
from wifi.main_server import WifiServer


transport_layer_options = {
    "TCP continuous": 'K',
    "TCP discontinuous":'T',
    "UDP":'U',
    "BLE continuous":'C',
    "BLE discontinuous":'D',
}

reverse_transport_layer_options = {
    'K':"TCP continuous",
    'T':"TCP discontinuous",
    'U':"UDP",
    'C':"BLE continuous",
    'D':"BLE discontinuous",
}

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(743, 957)
        self.Pestana_principal = QtWidgets.QTabWidget(Dialog)
        self.Pestana_principal.setGeometry(QtCore.QRect(0, 0, 741, 951))
        self.Pestana_principal.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.Pestana_principal.setObjectName("Pestana_principal")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.groupBox = QtWidgets.QGroupBox(self.tab)
        self.groupBox.setGeometry(QtCore.QRect(40, 10, 651, 261))
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.groupBox_2 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName("gridLayout")
        self.label_20 = QtWidgets.QLabel(self.groupBox_2)
        self.label_20.setObjectName("label_20")
        self.gridLayout.addWidget(self.label_20, 4, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.groupBox_2)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 0, 0, 1, 1)
        self.gyro_sens_text = QtWidgets.QTextEdit(self.groupBox_2)
        self.gyro_sens_text.setObjectName("gyro_sens_text")
        self.gridLayout.addWidget(self.gyro_sens_text, 3, 1, 1, 1)
        self.acc_sampl_text = QtWidgets.QTextEdit(self.groupBox_2)
        self.acc_sampl_text.setObjectName("acc_sampl_text")
        self.gridLayout.addWidget(self.acc_sampl_text, 0, 1, 1, 1)
        self.bme_sampling_text = QtWidgets.QTextEdit(self.groupBox_2)
        self.bme_sampling_text.setObjectName("bme_sampling_text")
        self.gridLayout.addWidget(self.bme_sampling_text, 4, 1, 1, 1)
        self.label_27 = QtWidgets.QLabel(self.groupBox_2)
        self.label_27.setObjectName("label_27")
        self.gridLayout.addWidget(self.label_27, 6, 0, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.groupBox_2)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 3, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.groupBox_2)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 2, 0, 1, 1)
        self.disc_time_text = QtWidgets.QTextEdit(self.groupBox_2)
        self.disc_time_text.setObjectName("disc_time_text")
        self.gridLayout.addWidget(self.disc_time_text, 6, 1, 1, 1)
        self.acc_sens_text = QtWidgets.QTextEdit(self.groupBox_2)
        self.acc_sens_text.setObjectName("acc_sens_text")
        self.gridLayout.addWidget(self.acc_sens_text, 2, 1, 1, 1)
        self.gridLayout_5.addWidget(self.groupBox_2, 0, 0, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_10 = QtWidgets.QLabel(self.groupBox_3)
        self.label_10.setObjectName("label_10")
        self.gridLayout_3.addWidget(self.label_10, 1, 0, 1, 1)
        self.label_28 = QtWidgets.QLabel(self.groupBox_3)
        self.label_28.setObjectName("label_28")
        self.gridLayout_3.addWidget(self.label_28, 4, 0, 1, 1)
        self.host_ip_text = QtWidgets.QTextEdit(self.groupBox_3)
        self.host_ip_text.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.host_ip_text.setObjectName("host_ip_text")
        self.gridLayout_3.addWidget(self.host_ip_text, 2, 5, 1, 1)
        self.label_26 = QtWidgets.QLabel(self.groupBox_3)
        self.label_26.setObjectName("label_26")
        self.gridLayout_3.addWidget(self.label_26, 3, 0, 1, 1)
        self.tcp_port_text = QtWidgets.QTextEdit(self.groupBox_3)
        self.tcp_port_text.setMaximumSize(QtCore.QSize(16777215, 47))
        self.tcp_port_text.setObjectName("tcp_port_text")
        self.gridLayout_3.addWidget(self.tcp_port_text, 0, 5, 1, 1)
        self.udp_port_text = QtWidgets.QTextEdit(self.groupBox_3)
        self.udp_port_text.setObjectName("udp_port_text")
        self.gridLayout_3.addWidget(self.udp_port_text, 1, 5, 1, 1)
        self.text_ssid = QtWidgets.QTextEdit(self.groupBox_3)
        self.text_ssid.setObjectName("text_ssid")
        self.gridLayout_3.addWidget(self.text_ssid, 3, 5, 1, 1)
        self.password_text = QtWidgets.QTextEdit(self.groupBox_3)
        self.password_text.setObjectName("password_text")
        self.gridLayout_3.addWidget(self.password_text, 4, 5, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.groupBox_3)
        self.label_8.setObjectName("label_8")
        self.gridLayout_3.addWidget(self.label_8, 0, 0, 1, 2)
        self.label_12 = QtWidgets.QLabel(self.groupBox_3)
        self.label_12.setObjectName("label_12")
        self.gridLayout_3.addWidget(self.label_12, 2, 0, 1, 3)
        self.gridLayout_5.addWidget(self.groupBox_3, 0, 1, 1, 1)
        self.groupBox_4 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_4.setGeometry(QtCore.QRect(40, 280, 661, 351))
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.progress_bar = QtWidgets.QProgressBar(self.groupBox_4)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setObjectName("progress_bar")
        self.gridLayout_9.addWidget(self.progress_bar, 11, 1, 1, 2)
        self.groupBox_6 = QtWidgets.QGroupBox(self.groupBox_4)
        self.groupBox_6.setObjectName("groupBox_6")
        self.gridLayout_10 = QtWidgets.QGridLayout(self.groupBox_6)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.esp_ble_select = QtWidgets.QComboBox(self.groupBox_6)
        self.esp_ble_select.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.esp_ble_select.setObjectName("esp_ble_select")
        self.gridLayout_10.addWidget(self.esp_ble_select, 0, 0, 1, 2)
        self.start_ble_button = QtWidgets.QPushButton(self.groupBox_6)
        self.start_ble_button.setStyleSheet("background-color: rgb(5, 5, 203);\n"
                                            "color: rgb(255, 255, 255);")
        self.start_ble_button.setObjectName("start_ble_button")

        self.esp_ble_scan_button = QtWidgets.QPushButton(self.groupBox_6)
        self.esp_ble_scan_button.setStyleSheet("background-color: rgb(5, 5, 203);\n"
                                            "color: rgb(255, 255, 255);")
        self.esp_ble_scan_button.setObjectName("esp_ble_scan_button")

        self.gridLayout_10.addWidget(self.esp_ble_scan_button, 0, 2, 1, 1)
        self.gridLayout_10.addWidget(self.start_ble_button,  1, 0, 1, 3)

        self.gridLayout_9.addWidget(self.groupBox_6, 2, 1, 2, 2)
        self.label_29 = QtWidgets.QLabel(self.groupBox_4)
        self.label_29.setStyleSheet("color: rgb(0, 0, 0);\n"
                                    "\n"
                                    "")
        self.label_29.setObjectName("label_29")
        self.gridLayout_9.addWidget(self.label_29, 0, 1, 1, 1)
        self.label_30 = QtWidgets.QLabel(self.groupBox_4)
        self.label_30.setStyleSheet("color: rgb(0, 0, 0);\n"
                                    "\n"
                                    "")
        self.label_30.setObjectName("label_30")
        self.gridLayout_9.addWidget(self.label_30, 1, 1, 1, 1)
        self.transport_layer_select = QtWidgets.QComboBox(self.groupBox_4)
        self.transport_layer_select.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.transport_layer_select.setObjectName("transport_layer_select")
        self.transport_layer_select.addItem("")
        self.transport_layer_select.addItem("")
        self.transport_layer_select.addItem("")
        self.transport_layer_select.addItem("")
        self.transport_layer_select.addItem("")
        self.gridLayout_9.addWidget(self.transport_layer_select, 0, 2, 1, 1)
        self.protocol_id_select = QtWidgets.QComboBox(self.groupBox_4)
        self.protocol_id_select.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.protocol_id_select.setObjectName("protocol_id_select")
        self.protocol_id_select.addItem("")
        self.protocol_id_select.addItem("")
        self.protocol_id_select.addItem("")
        self.protocol_id_select.addItem("")
        self.protocol_id_select.addItem("")
        self.gridLayout_9.addWidget(self.protocol_id_select, 1, 2, 1, 1)
        # self.disconnect_button = QtWidgets.QPushButton(self.groupBox_4)
        # self.disconnect_button.setStyleSheet("background-color: rgb(103, 8, 8);\n"
        #                                      "color: rgb(255, 255, 255);")
        # self.disconnect_button.setObjectName("disconnect_button")
        # self.gridLayout_9.addWidget(self.disconnect_button, 10, 1, 1, 2)
        self.groupBox_9 = QtWidgets.QGroupBox(self.groupBox_4)
        self.groupBox_9.setObjectName("groupBox_9")
        self.gridLayout_11 = QtWidgets.QGridLayout(self.groupBox_9)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.start_wifi_server_button = QtWidgets.QPushButton(self.groupBox_9)
        self.start_wifi_server_button.setStyleSheet("background-color: rgb(5, 5, 203);\n"
                                                    "color: rgb(255, 255, 255);")
        self.start_wifi_server_button.setObjectName("start_wifi_server_button")
        self.gridLayout_11.addWidget(self.start_wifi_server_button, 0, 0, 1, 1)
        self.gridLayout_9.addWidget(self.groupBox_9, 8, 1, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_9.addItem(spacerItem, 9, 1, 1, 1)
        self.groupBox_10 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_10.setGeometry(QtCore.QRect(40, 640, 651, 251))
        self.groupBox_10.setObjectName("groupBox_10")
        self.gridLayout_12 = QtWidgets.QGridLayout(self.groupBox_10)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.console_output = QtWidgets.QTextBrowser(self.groupBox_10)
        self.console_output.setObjectName("console_output")
        self.gridLayout_12.addWidget(self.console_output, 0, 0, 1, 1)
        self.groupBox_10.raise_()
        self.groupBox_4.raise_()
        self.groupBox.raise_()
        self.Pestana_principal.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.groupBox_5 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_5.setGeometry(QtCore.QRect(20, 0, 681, 891))
        self.groupBox_5.setObjectName("groupBox_5")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_5)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.plot1_select = QtWidgets.QComboBox(self.groupBox_5)
        self.plot1_select.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.plot1_select.setObjectName("plot1_select")
        self.plot1_select.addItem("")
        self.plot1_select.addItem("")
        self.plot1_select.addItem("")
        self.plot1_select.addItem("")
        self.plot1_select.addItem("")
        self.plot1_select.addItem("")
        self.gridLayout_4.addWidget(self.plot1_select, 0, 0, 1, 1)

        # self.plot1 = QtWidgets.QWidget(self.groupBox_5)
        # self.plot1.setObjectName("plot1")
        self.plot1_figure = Figure()
        self.plot1 = FigureCanvas(self.plot1_figure)

        self.gridLayout_4.addWidget(self.plot1, 1, 0, 1, 1)
        self.plot2_select = QtWidgets.QComboBox(self.groupBox_5)
        self.plot2_select.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.plot2_select.setObjectName("plot2_select")
        self.plot2_select.addItem("")
        self.plot2_select.addItem("")
        self.plot2_select.addItem("")
        self.plot2_select.addItem("")
        self.plot2_select.addItem("")
        self.plot2_select.addItem("")
        self.gridLayout_4.addWidget(self.plot2_select, 2, 0, 1, 1)

        # self.plot2 = QtWidgets.QWidget(self.groupBox_5)
        # self.plot2.setObjectName("plot2")
        self.plot2_figure = Figure()
        self.plot2 = FigureCanvas(self.plot2_figure)

        self.gridLayout_4.addWidget(self.plot2, 3, 0, 1, 1)
        self.plot3_select = QtWidgets.QComboBox(self.groupBox_5)
        self.plot3_select.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.plot3_select.setObjectName("plot3_select")
        self.plot3_select.addItem("")
        self.plot3_select.addItem("")
        self.plot3_select.addItem("")
        self.plot3_select.addItem("")
        self.plot3_select.addItem("")
        self.plot3_select.addItem("")
        self.gridLayout_4.addWidget(self.plot3_select, 4, 0, 1, 1)

        # self.plot3 = QtWidgets.QWidget(self.groupBox_5)
        # self.plot3.setObjectName("plot3")
        self.plot3_figure = Figure()
        self.plot3 = FigureCanvas(self.plot3_figure)

        self.gridLayout_4.addWidget(self.plot3, 5, 0, 1, 1)
        self.plot1.raise_()
        self.plot1_select.raise_()
        self.plot2.raise_()
        self.plot3.raise_()
        self.plot3_select.raise_()
        self.plot2_select.raise_()
        self.Pestana_principal.addTab(self.tab_2, "")

        self.retranslateUi(Dialog)
        self.Pestana_principal.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBox.setTitle(_translate("Dialog", "Configurations"))
        self.groupBox_2.setTitle(_translate("Dialog", "Sensor"))
        self.label_20.setText(_translate("Dialog", "BME688 Sampling"))
        self.label_7.setText(_translate("Dialog", "Acc Sampling"))
        self.label_27.setText(_translate("Dialog", "Discontinuos time"))
        self.label_11.setText(_translate("Dialog", "Gyro Sensibility"))
        self.label_9.setText(_translate("Dialog", "Acc Sensibility"))
        self.groupBox_3.setTitle(_translate("Dialog", "Network"))
        self.label_10.setText(_translate("Dialog", "UDP Port"))
        self.label_28.setText(_translate("Dialog", "Password"))
        self.label_26.setText(_translate("Dialog", "SSID"))
        self.label_8.setText(_translate("Dialog", " TCP Port"))
        self.label_12.setText(_translate("Dialog", "Host IP Addr"))
        self.groupBox_4.setTitle(_translate("Dialog", "Connection"))
        self.groupBox_6.setTitle(_translate("Dialog", "BLE"))
        self.start_ble_button.setText(_translate("Dialog", "Configure via BLE"))
        self.esp_ble_scan_button.setText(_translate("Dialog", "Scan"))
        self.label_29.setText(_translate("Dialog", "Transport Layer"))
        self.label_30.setText(_translate("Dialog", "Protocol ID"))
        self.transport_layer_select.setItemText(0, _translate("Dialog", "TCP continuous"))
        self.transport_layer_select.setItemText(1, _translate("Dialog", "TCP discontinuous"))
        self.transport_layer_select.setItemText(2, _translate("Dialog", "UDP"))
        self.transport_layer_select.setItemText(3, _translate("Dialog", "BLE continuous"))
        self.transport_layer_select.setItemText(4, _translate("Dialog", "BLE discontinuous"))
        self.protocol_id_select.setItemText(0, _translate("Dialog", "1"))
        self.protocol_id_select.setItemText(1, _translate("Dialog", "2"))
        self.protocol_id_select.setItemText(2, _translate("Dialog", "3"))
        self.protocol_id_select.setItemText(3, _translate("Dialog", "4"))
        self.protocol_id_select.setItemText(4, _translate("Dialog", "5"))
        # self.disconnect_button.setText(_translate("Dialog", "Disconnect"))
        self.groupBox_9.setTitle(_translate("Dialog", "WIFI"))
        self.start_wifi_server_button.setText(_translate("Dialog", "Start Wi-Fi Server"))
        self.groupBox_10.setTitle(_translate("Dialog", "Console"))
        self.Pestana_principal.setTabText(self.Pestana_principal.indexOf(
            self.tab), _translate("Dialog", "Config and Connection"))
        self.groupBox_5.setTitle(_translate("Dialog", "Data"))
        self.Pestana_principal.setTabText(self.Pestana_principal.indexOf(
            self.tab_2), _translate("Dialog", "Data"))


class App(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        DatabaseManager.db_init()
        self.ui.console_output.setStyleSheet("background-color: #2b2b2b;")
        self.data_sources = {
            "Temperatura": [],
            "Humedad": [],
            "Acc_x": [],
            "Acc_y": [],
            "Acc_z": [],
        }
   


        self.plots = [
            {
                "figure": self.ui.plot1_figure,
                "idx": 0,
                "canvas": self.ui.plot1,
                "data": "Temperatura",
                "select": self.ui.plot1_select,
            },
            {
                "figure": self.ui.plot2_figure,
                "idx": 1,
                "canvas": self.ui.plot2,
                "data": "Humedad",
                "select": self.ui.plot2_select,
            },
            {
                "figure": self.ui.plot3_figure,
                "idx": 2,
                "canvas": self.ui.plot3,
                "data": "Acc_x",
                "select": self.ui.plot3_select,
            },

        ]
        _translate = QtCore.QCoreApplication.translate
        for plot in self.plots:
            for i,key in enumerate(self.data_sources.keys()):
                plot["select"].setItemText(i, _translate("Dialog", key))

        self.update_graphs()

        # self.gyro_sens_text = QtWidgets.QTextEdit(self.groupBox_2)
        # add function on change
        self.populate_config_text()
        
        self.config_components_text = [
            self.ui.acc_sampl_text,
            self.ui.acc_sens_text,
            self.ui.gyro_sens_text,
            self.ui.bme_sampling_text,
            self.ui.disc_time_text,
            self.ui.host_ip_text,
            self.ui.tcp_port_text,
            self.ui.udp_port_text,
            self.ui.password_text,
            self.ui.text_ssid,
        ]

        self.config_components_combo = [
            self.ui.transport_layer_select,
            self.ui.protocol_id_select,
        ]
        for component in self.config_components_text:
            component.textChanged.connect(self.on_change_config)

        for component in self.config_components_combo:
            component.currentIndexChanged.connect(self.on_change_config)
            
        self.worker = self.GraphUpdateWorker(self.update)
        self.ble_list = []
        self.ui.start_ble_button.clicked.connect(self.run_ble_service)
        self.ui.start_wifi_server_button.clicked.connect(self.run_wifi_service)
        self.current_service_thread = None

        


    
    class GraphUpdateWorker(QtCore.QObject): 
        def __init__(self, target_function, parent=None):
            super().__init__(parent)
            self.target_function = target_function
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.run)
            self.timer.start(1)  

        def run(self):
            self.target_function()



    def load_progress(self):
        for i in range(101):
            time.sleep(0.05)
            self.ui.progress_bar.setValue(i)

    def run_ble_service(self):

        self.current_service_thread = BleClient(self.current_ble_addr).run(join = False)
        self.load_progress()


    def run_wifi_service(self):

        self.current_service_thread = WifiServer().run(join = False)
        self.load_progress()
    
    def disconnect(self):
        if self.current_service_thread is not None:
            self.current_service_thread.terminate()
            self.current_service_thread = None
            console.print("Disconnected", style="info")

    def on_change_config(self):        
        transport_layer = transport_layer_options[self.ui.transport_layer_select.currentText()]
        protocol_id = self.ui.protocol_id_select.currentText()
        
        DatabaseManager.update_config(bmi270_gyro_sensibility = int(self.ui.gyro_sens_text.toPlainText()),
                                      bmi270_sampling = int(self.ui.acc_sampl_text.toPlainText()),
                                      bme688_sampling = int(self.ui.bme_sampling_text.toPlainText()),
                                      discontinuous_time = int(self.ui.disc_time_text.toPlainText()),
                                      bmi270_sensibility = int(self.ui.acc_sens_text.toPlainText()),
                                      host_ip_addr = str(self.ui.host_ip_text.toPlainText()),
                                      tcp_port = str(self.ui.tcp_port_text.toPlainText()),
                                      udp_port = str(self.ui.udp_port_text.toPlainText()),
                                      password = str(self.ui.password_text.toPlainText()),
                                      ssid = str(self.ui.text_ssid.toPlainText()),                                      
                                      transport_layer = str(transport_layer),
                                      protocol_id = str(protocol_id)
                                    )
        
                
        console.print("Config Updated", style="info")
        console.print(DatabaseManager.get_default_config(), style="info")


    def populate_config_text(self):
        cur_config = DatabaseManager.get_default_config()
        
        self.ui.gyro_sens_text.setText(str(cur_config.bmi270_gyro_sensibility))
        self.ui.acc_sampl_text.setText(str(cur_config.bmi270_sampling))
        self.ui.bme_sampling_text.setText(str(cur_config.bme688_sampling))
        self.ui.disc_time_text.setText(str(cur_config.discontinuous_time))
        self.ui.acc_sens_text.setText(str(cur_config.bmi270_sensibility))
        self.ui.host_ip_text.setText(str(cur_config.host_ip_addr))
        self.ui.tcp_port_text.setText(str(cur_config.tcp_port))
        self.ui.udp_port_text.setText(str(cur_config.udp_port))
        self.ui.password_text.setText(str(cur_config.password))
        

        current_transport_layer_select_option = reverse_transport_layer_options[cur_config.transport_layer]
        current_protocol_id_select_option = cur_config.protocol_id

        self.ui.protocol_id_select.setCurrentText(str(current_protocol_id_select_option))
        self.ui.transport_layer_select.setCurrentText(str(current_transport_layer_select_option))        


        self.ui.text_ssid.setText(str(cur_config.ssid))

        self.ui.esp_ble_scan_button.clicked.connect(self.update_ble_list)
    
    @property
    def current_ble_addr(self):
        return self.ble_list[self.ui.esp_ble_select.currentIndex()][1]



    def update_ble_list(self):
        devices = asyncio.run(self.discover())
        devices_list = [(device.name, device.address) for device in devices]
        self.ble_list = devices_list
        self.update_ble_select()
    
    
    def update_ble_select(self):
        self.ui.esp_ble_select.clear()
        for device in self.ble_list:
            text = f"{device[0]} - {device[1]}"
            self.ui.esp_ble_select.addItem(text)

    async def discover(self):
        scanner = BleakScanner()
        devices = await scanner.discover()
        return devices

    def update_console(self):
        current_output_html = console.export_html(clear = False )
        self.ui.console_output.setHtml(current_output_html)
        self.ui.console_output.moveCursor(QtGui.QTextCursor.End)

    def update_data_sources(self):


        # read the current selection for plot combo box
        # update plots data sources
        for plot in self.plots:
            select = plot["select"]
            plot["data"] = select.currentText()
        



        latest_data = DatabaseManager.get_latest_data(200)
       
        for _,source in self.data_sources.items():
            source.clear()

        for entry in latest_data:
            if entry.temp is not None:
                self.data_sources["Temperatura"].append(int(entry.temp))

            if entry.hum is not None:
                self.data_sources["Humedad"].append(int(entry.hum))
            
            if entry.ACC_X is not None:
                acc_x_blob = entry.ACC_X
                acc_y_blob = entry.ACC_Y
                acc_z_blob = entry.ACC_Z

                acc_x = struct.unpack('f', acc_x_blob[:4])[0]
                acc_y = struct.unpack('f', acc_y_blob[:4])[0]
                acc_z = struct.unpack('f', acc_z_blob[:4])[0]
                            
                self.data_sources["Acc_x"].append(acc_x)
                self.data_sources["Acc_y"].append(acc_y)
                self.data_sources["Acc_z"].append(acc_z)
            

        #print data sources

        
        # append every elemnt of every row to the corresponding data source
            

    def update(self):
        self.update_console()
        self.update_data_sources()
        self.update_graphs()
    
    def update_graphs(self):
        for plot in self.plots:
            plot["figure"].clear()
            axes = plot["figure"].add_subplot(111)
            y_data = self.data_sources[plot["data"]]
            axes.plot(y_data)
            axes.set_xlabel("Time")
            axes.set_ylabel(plot["data"])
            axes.set_title(plot["data"])
            plot["canvas"].draw()



if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = App()
    window.show()
    app.exec()