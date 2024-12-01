import serial
import crcmod
import struct
import openpyxl
import traceback
import xlsxwriter
from datetime import datetime,timezone
# from PyQt5
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtGui import QColor,QIcon
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QTableWidgetItem,QFileDialog)
def CRC(input):
    crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)
    # print (crc16(b"1234").to_bytes(2,"big",signed=False)
    a = crc16(input).to_bytes(2, "little")
    return a
def read_data(port,SlaveID,RegAddress_list,RegCount_list,Type_list,timeout,baudrat=9600,key="big",revers_float=False):
    # SlaveID = 1
    # key = 1032
    # RegAddress_list = [0, 836, 834, 838, 78, 82, 810, 806, 548]
    # NameOfAddress_list = ['version', 'p', 't', 'c', 'co2', 'n2', 'vb', 'vm', 'Bat day']
    # RegCount_list = [4, 2, 2, 2, 2, 2, 2, 2, 1]
    # Type_list = ['str', 'f', 'f', 'f', 'f', 'f', 'u32', 'u32', 'u16']
    # port = valid_ports[comID]
    values=[]
    # RegAddress_list=[810]
    # NameOfAddress_list=['vm']
    try:
        ser = serial.Serial(port, baudrat, timeout=timeout/1000, stopbits=1, parity=serial.PARITY_NONE,writeTimeout=0.1)
    except:
        return ("Port Failed")
    #ser.write(b'012345')
    #s = ser.read(10)
    for counter in range(RegAddress_list.__len__()):
        try:
            RegAddress = int(RegAddress_list[counter])
        except:
            return ("Wrong Address  --> Index : "+str(counter+1))
        try:
            RegCount = int(RegCount_list[counter])
        except:
            return ("Wrong RegCount  --> Index : "+str(counter+1))
        text = SlaveID.to_bytes(1, "big")
        text += b"\x03"
        text += RegAddress.to_bytes(2, "big")
        text += RegCount.to_bytes(2, "big")
        crc = CRC(text)
        text += crc
        # print(text)

        # read up to one hundred bytes
        try:
            ser.write(text)
            print("transmited : ")
            print(text)
            print(list(text))
        except Exception as exception:
            traceback.print_exc()
        s = ser.read(5 + RegCount * 2)
        # FileNotFoundError                   # or as much is in the buffer
        # PermissionError
        # print(s)

        print("----------------------")
        print("recieved : ")
        print(s)
        print(list(s))
        print("*************************************************")
        if(s.__len__()!=(5 + RegCount * 2)):
            values.append("invalid")
            print("count")
            continue
        if(s[0]!=SlaveID):
            values.append("invalid")
            print("ID")
            continue
        if(s[1] != 3):#function code
            values.append("invalid")
            print("function")
            continue
        crc = CRC(s[0:3 + RegCount * 2])
        if (crc == s[3 + RegCount * 2:5 + RegCount * 2]):
            # print("crc_ok")
            byte_val = s[3:3 + RegCount * 2]
            # print(byte_val)
            if (Type_list[counter] == 'f'):
                if(RegCount!=2):return ("Wrong RegCount  --> Index : "+str(counter+1))
                new_byte = b''
                # new_byte += byte_val[key // 1000].to_bytes(1, "big")
                # new_byte += byte_val[(key % 1000 // 100)].to_bytes(1, "big")
                # new_byte += byte_val[(key % 100 // 10)].to_bytes(1, "big")
                # new_byte += byte_val[key % 10].to_bytes(1, "big")
                byte_val=byte_val[::-1]
                if  revers_float:
                    new_byte=byte_val
                else:
                    new_byte=byte_val[2:4]+byte_val[0:2]
                float_val = struct.unpack('f', new_byte[:4])
                # print(str(RegAddress_list[counter]) + ' --> ' + str(NameOfAddress_list[counter]) + ' : ' + str(
                #     round(float(float_val[0]), 2)))
                values.append(str(round(float(float_val[0]), 5)))
                continue
            if (Type_list[counter] == 'u32'):
                if(RegCount!=2):return ("Wrong RegCount  --> Index : "+str(counter+1))
                new_byte = 0
                # new_byte += byte_val[0] << 24
                # new_byte += byte_val[1] << 16
                # new_byte += byte_val[2] << 8
                # new_byte += byte_val[3]

                # new_byte += byte_val[(key % 1000 // 100)]<< 24
                # new_byte += byte_val[key // 1000]<<16
                # new_byte += byte_val[key % 10]<< 8
                # new_byte += byte_val[(key % 100 // 10)]
                
                new_byte=int.from_bytes(byte_val[:4],key)

                # print(str(RegAddress_list[counter]) + ' --> ' + str(NameOfAddress_list[counter]) + ' : ' + str(new_byte))
                values.append(str(new_byte))
                continue
            if (Type_list[counter] == 'hex'):
                # if(RegCount!=2):return ("Wrong RegCount  --> Index : "+str(counter+1))
                new_byte = 0
                
                new_byte=int.from_bytes(byte_val,key)

                # print(str(RegAddress_list[counter]) + ' --> ' + str(NameOfAddress_list[counter]) + ' : ' + str(new_byte))
                values.append(str(hex(new_byte)))
                continue
            if (Type_list[counter] == 'bin'):
                # if(RegCount!=2):return ("Wrong RegCount  --> Index : "+str(counter+1))
                new_byte = 0
                
                new_byte=int.from_bytes(byte_val,key)

                # print(str(RegAddress_list[counter]) + ' --> ' + str(NameOfAddress_list[counter]) + ' : ' + str(new_byte))
                values.append(str(bin(new_byte)))
                continue
            if (Type_list[counter] == 'u16'):
                if(RegCount!=1):return ("Wrong RegCount  --> Index : "+str(counter+1))
                # new_byte = 0
                # if((key // 1000)==1 or (key // 1000)==3):
                #     new_byte += byte_val[0]  << 8
                #     new_byte += byte_val[1]
                # else:
                #     new_byte += byte_val[1]  << 8
                #     new_byte += byte_val[0]
                # # print( str(RegAddress_list[counter]) + ' --> ' + str(NameOfAddress_list[counter]) + ' : ' + str(new_byte))

                new_byte=int.from_bytes(byte_val[:2],key)
                values.append(str(new_byte))
                continue

            if (Type_list[counter] == 'date'):
                if(RegCount!=2):return ("Wrong RegCount  --> Index : "+str(counter+1))

                # print(int(byte_val[0]),int(byte_val[1]),int(byte_val[2]),int(byte_val[3]))
                # new_byte = 0
                # new_byte += byte_val[(key % 1000 // 100)]<< 24
                # new_byte += byte_val[key // 1000]<<16
                # new_byte += byte_val[key % 10]<< 8
                # new_byte += byte_val[(key % 100 // 10)]
                new_byte=int.from_bytes(byte_val[:4],key)
                date=datetime.fromtimestamp(new_byte,tz=timezone.utc)
                values.append(str(date.month)+'/'+str(date.day)+'/'+str(date.year)+"   "+str(date.hour)+':'+str(date.minute)+":"+str(date.second))
                continue
            if (Type_list[counter] == 'str'):
                # print(str(RegAddress_list[counter]) + ' --> ' + str(NameOfAddress_list[counter]) + ' : ' + str(byte_val.decode('utf8')))
                values.append(str(byte_val.decode('utf8')))
                continue
            if (Type_list[counter] == 'index'):
                if(RegCount!=4):return ("Wrong RegCount  --> Index : "+str(counter+1))
                print(byte_val)
                new_byte = 0
                # new_byte += byte_val[3] << 24
                # new_byte += byte_val[2] << 16
                # new_byte += byte_val[1] << 8
                # new_byte += byte_val[0]
                new_byte += byte_val[key % 10]<< 24
                new_byte += byte_val[(key % 100 // 10)]<< 16
                new_byte += byte_val[(key % 1000 // 100)]<< 8
                new_byte += byte_val[key // 1000]

                new_byte1=0
                new_byte1 += byte_val[4+(key % 10)]<< 24
                new_byte1 += byte_val[4+((key % 100 )// 10)]<< 16
                new_byte1 += byte_val[4+((key % 1000 )// 100)]<< 8
                new_byte1 += byte_val[4+(key // 1000)]

                
                new_byte=int.from_bytes(byte_val[:4],key)
                
                new_byte1=int.from_bytes(byte_val[4:8],key)
                # new_byte1 += byte_val[7] << 24
                # new_byte1 += byte_val[6] << 16
                # new_byte1 += byte_val[5] << 8
                # new_byte1 += byte_val[4]
                DEC_FRAC =100000000
                print(new_byte,new_byte1)
                # print(str(RegAddress_list[counter]) + ' --> ' + str(NameOfAddress_list[counter]) + ' : ' + str(new_byte))
                values.append(str(round(float(new_byte+(new_byte1/DEC_FRAC)), 4)))
                continue
            return ("Wrong Type  --> Index : "+str(counter+1))
        else:
            # print(str(RegAddress_list[counter]) + ' --> ' + str(NameOfAddress_list[counter]) + ' : ' + "invalid")
            values.append("invalid")
            print("CRC")
    return values

class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)
        self.counter=0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.originalPalette = QApplication.palette()

        self.styleComboBox = QComboBox()
        self.comportbutton=QPushButton("Ports")
        self.comportbutton.clicked.connect(self.Search_Ports)

        self.baudComboBox = QComboBox()
        self.baudComboBox.addItem("1200")
        self.baudComboBox.addItem("2400")
        self.baudComboBox.addItem("4800")
        self.baudComboBox.addItem("9600")
        self.baudComboBox.addItem("19200")
        self.baudComboBox.setCurrentIndex(3)
        self.Save_Config=QPushButton("Save Config")
        self.Save_Config.clicked.connect(self.SaveConfig)
        self.Open_Config=QPushButton("Open Config")
        self.Open_Config.clicked.connect(self.OpenConfig)

        styleLabel = QLabel("&Com&Port:")
        styleLabel.setBuddy(self.styleComboBox)
        #self.useStylePaletteCheckBox = QCheckBox("&Use style's standard palette")
        #self.useStylePaletteCheckBox.setChecked(True)

        #disableWidgetsCheckBox = QCheckBox("&Disable widgets")

        # self.createTopLeftGroupBox()
        self.createRightBox()
        self.createLeftTabWidget()
        # self.createBottomRightGroupBox()
        # self.createProgressBar()

        self.styleComboBox.textActivated.connect(self.changeStyle)
        #self.useStylePaletteCheckBox.toggled.connect(self.changePalette)
        # disableWidgetsCheckBox.toggled.connect(self.topLeftGroupBox.setDisabled)
        # disableWidgetsCheckBox.toggled.connect(self.topRightGroupBox.setDisabled)
        # disableWidgetsCheckBox.toggled.connect(self.bottomLeftTabWidget.setDisabled)
        # disableWidgetsCheckBox.toggled.connect(self.bottomRightGroupBox.setDisabled)

        topLayout = QHBoxLayout()
        topLayout.addWidget(styleLabel)
        topLayout.addWidget(self.styleComboBox)
        topLayout.addWidget(self.comportbutton)
        topLayout.addWidget(self.baudComboBox)
        topLayout.addWidget(QLabel("     8-N-1        "))
        topLayout.addWidget(QLabel("                  "))
        topLayout.addWidget(QLabel("                  "))
        topLayout.addWidget(QLabel("                  "))
        topLayout.addWidget(self.Save_Config)
        topLayout.addWidget(self.Open_Config)
        topLayout.addStretch(1)
        #topLayout.addWidget(self.useStylePaletteCheckBox)
        # topLayout.addWidget(disableWidgetsCheckBox)

        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        # mainLayout.addWidget(self.topLeftGroupBox, 1, 0)
        mainLayout.addWidget(self.tableWidget, 1, 0)
        mainLayout.addWidget(self.RightGroupBox, 1, 1)
        # mainLayout.addWidget(self.bottomRightGroupBox, 2, 1)
        # mainLayout.addWidget(self.progressBar, 3, 0, 1, 2)
        # mainLayout.setRowStretch(1, 1)
        # mainLayout.setRowStretch(2, 1)
        # mainLayout.setColumnStretch(0, 1)
        # mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("Modbus Pull")
        self.setWindowIcon(QIcon("img/Icon.ico"))
        self.changeStyle('Fusion')

    def Search_Ports(self):

        self.styleComboBox.clear()
        port_name = "COM"
        valid_ports = []
        for i in range(100):
            port = port_name + str(i)
            try:
                ser = serial.Serial(port)
                valid_ports.append(port)
                ser.close()
            except Exception as er:
                if ("Access is denied" in er.__str__()):
                    valid_ports.append(port + "(busy)")
            except serial.serialutil.SerialException:
                # print(serial.serialutil.SerialException)
                # print(port+"(busy)")
                continue
        for port in valid_ports:
            self.styleComboBox.addItem(port)
    def SaveConfig(self):
        name=[]
        value=[]
        address = []
        regcount = []
        type_ = []
        for r in range(self.tableWidget.rowCount()):
            try:
                name_item = self.tableWidget.takeItem(r, 0)
                value_item = self.tableWidget.takeItem(r, 1)
                address_item = self.tableWidget.takeItem(r, 2)
                regcount_item = self.tableWidget.takeItem(r, 3)
                type_item = self.tableWidget.takeItem(r, 4)
                try:
                    name.append(name_item.text())
                except:
                    name.append("")
                try:
                    value.append(value_item.text())
                except:
                    value.append("")
                address.append(int(address_item.text()))
                regcount.append(int(regcount_item.text()))
                type_.append(type_item.text())
                self.tableWidget.setItem(r, 0, name_item)
                self.tableWidget.setItem(r, 1, value_item)
                self.tableWidget.setItem(r, 2, address_item)
                self.tableWidget.setItem(r, 3, regcount_item)
                self.tableWidget.setItem(r, 4, type_item)
            except :
                break
        dialog = QFileDialog(self)
        filename,_=dialog.getSaveFileName(caption='Save Configuratin',filter='(*.xlsx)')
        if(filename):
            workbook = xlsxwriter.Workbook(filename)

            # The workbook object is then used to add new
            # worksheet via the add_worksheet() method.
            worksheet = workbook.add_worksheet()

            # Use the worksheet object to write
            # data via the write() method.

            # Finally, close the Excel file
            # via the close() method.
            worksheet.write('A1' , 'Name')
            worksheet.write('B1' , 'Value')
            worksheet.write('C1' , 'Address')
            worksheet.write('D1' , 'Regcount')
            worksheet.write('E1' , 'Type')
            for i in range(self.tableWidget.rowCount()):
                try:

                    worksheet.write('A'+str(i+2), str(name[i]))
                    worksheet.write('B'+str(i+2), str(value[i]))
                    worksheet.write('C'+str(i+2), str(address[i]))
                    worksheet.write('D'+str(i+2), str(regcount[i]))
                    worksheet.write('E'+str(i+2), str(type_[i]))
                    # print(type(i))
                    # name_cell[i+1].value=
                    # address_cell[i+1].value =
                    # regcount_cell[i+1].value =
                    # type_cell[i+1].text =

                    # var_xls_TabSheet['a'+str(i)].value=name[i]
                except Exception as exception:
                    traceback.print_exc()
                    break
            workbook.close()
        # dialog.setWindowTitle()
        # dialog.setNameFilter()
        # dialog.setAcceptMode(QFileDialog.AcceptSave)
        # dialog.setFileMode(QFileDialog.AcceptMode)

        # dialog.setFileMode(QFileDialog.AcceptMode)
        # filename = None
        # if dialog.exec_() == QDialog.Accepted:
        #     filename = dialog.selectedFiles()
        # if filename:
        #     self.fname = str(filename[0])
        #     self.group_box.lineEdit.setText(self.fname)
    def OpenConfig(self):
        dialog = QFileDialog(self)
        filename, _ = dialog.getOpenFileName(caption='Open Configuratin', filter='(*.xlsx)')
        if (filename):
            self.tableWidget.clear()
            var_xls_FileOpen = openpyxl.load_workbook(filename)
            ary_xls_SheetNames = var_xls_FileOpen.get_sheet_names()
            var_xls_TabSheet = var_xls_FileOpen.get_sheet_by_name(ary_xls_SheetNames[0])
            name_cell = var_xls_TabSheet['a']
            address_cell = var_xls_TabSheet['c']
            regcount_cell = var_xls_TabSheet['d']
            type_cell = var_xls_TabSheet['e']
            name=[]
            address=[]
            regcount=[]
            type_=[]
            try:
                for i in range(self.tableWidget.rowCount()):
                    name.append(name_cell[i+1].value)
                    address.append(address_cell[i+1].value)
                    regcount.append(regcount_cell[i+1].value)
                    type_.append(type_cell[i+1].value)
            except:
                pass
            var_xls_FileOpen.close()
            for i in range(self.tableWidget.rowCount()):
                try:
                    self.tableWidget.setItem(i, 0, QTableWidgetItem(str(name[i])))
                    self.tableWidget.setItem(i, 2, QTableWidgetItem(str(address[i])))
                    self.tableWidget.setItem(i, 3, QTableWidgetItem(str(regcount[i])))
                    self.tableWidget.setItem(i, 4, QTableWidgetItem(str(type_[i])))
                except:
                    break
            
            self.tableWidget.setHorizontalHeaderLabels(["Name","Value","Address","RegCount","Type"])

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        # self.changePalette()

    # def changePalette(self):
    #     if (self.useStylePaletteCheckBox.isChecked()):
    #         QApplication.setPalette(QApplication.style().standardPalette())
    #     else:
    #         QApplication.setPalette(self.originalPalette)



    # def createTopLeftGroupBox(self):
    #     self.topLeftGroupBox = QGroupBox("Group 1")
    #
    #     radioButton1 = QRadioButton("Radio button 1")
    #     radioButton2 = QRadioButton("Radio button 2")
    #     radioButton3 = QRadioButton("Radio button 3")
    #     radioButton1.setChecked(True)
    #
    #     checkBox = QCheckBox("Tri-state check box")
    #     checkBox.setTristate(True)
    #     checkBox.setCheckState(Qt.CheckState.PartiallyChecked)
    #
    #     layout = QVBoxLayout()
    #     layout.addWidget(radioButton1)
    #     layout.addWidget(radioButton2)
    #     layout.addWidget(radioButton3)
    #     layout.addWidget(checkBox)
    #     layout.addStretch(1)
    #     self.topLeftGroupBox.setLayout(layout)
    def refresh_data(self):
        if(self.timer.isActive()):
            self.timer.killTimer(self.timer.timerId())
        address=[]
        regcount=[]
        type_=[]
        for i in range(100):
            try:
                address_item = self.tableWidget.takeItem(i, 2)
                regcount_item = self.tableWidget.takeItem(i, 3)
                type_item = self.tableWidget.takeItem(i, 4)
                if(address_item.text()=='' or regcount_item.text()=='' or type_item.text()==''):
                    break
                address.append(address_item.text())
                regcount.append(regcount_item.text())
                type_.append(type_item.text())
                self.tableWidget.setItem(i, 2,address_item)
                self.tableWidget.setItem(i, 3,regcount_item)
                self.tableWidget.setItem(i, 4,type_item)
            except:
                break
        try:
            vals=read_data(self.styleComboBox.currentText(),
                           int(self.spinBox_slavid.text()),
                           address,regcount,type_,
                           int(self.spinBox1.text()),
                           int(self.baudComboBox.currentText()),
                           self.keyComboBox.currentText(),
                           bool(self.floatReverseComboBox.currentText()=="True"))
        except Exception as exception:
            traceback.print_exc()
            self.Error.setText("Error\n"+"Can't Read Modbus")
            if (self.radioButton1.isChecked()):
                self.stop_auto_refresh()
            return
        if(type(vals)==str):
            self.Error.setText("Error\n"+vals)
            if (self.radioButton1.isChecked()):
                self.stop_auto_refresh()
            return
        else:
            self.Error.setText('')
        for i in range(vals.__len__()):
            try:
                _item = self.tableWidget.takeItem(i, 1)
                self.tableWidget.setItem(i, 1,QTableWidgetItem(str(vals[i])))
                self.tableWidget.item(i, 1).setBackground(QColor(225,225,225))
                if(str(vals[i])=="invalid"):
                    self.tableWidget.item(i, 1).setForeground(QColor(250, 50, 50))
                    continue
                if(str(_item.text())==str(vals[i])):
                    self.tableWidget.item(i, 1).setForeground(QColor(50, 50, 150))
                else:
                    self.tableWidget.item(i, 1).setForeground(QColor(150,50,250))
            except Exception as exception:
                traceback.print_exc()
                try:
                    self.tableWidget.setItem(i, 1, QTableWidgetItem(str(vals[i])))
                    self.tableWidget.item(i, 1).setBackground(QColor(225,225,225))
                    self.tableWidget.item(i, 1).setForeground(QColor(50, 50, 150))
                    if(str(vals[i])=="invalid"):
                        self.tableWidget.item(i, 1).setForeground(QColor(250, 50, 50))
                except:
                    break

        if(self.radioButton1.isChecked()):
            self.timer.start(self.spinBox2.value())
            if(self.Error.text()==''):
                self.counter+=1
                self.Error.setText("Counter\n"+str(self.counter))
        else:pass


        # self.tableWidget.setShowGrid(False)
    def Disable_All(self):
        self.spinBox_slavid.setDisabled(True)
        self.spinBox1.setDisabled(True)
        self.comportbutton.setDisabled(True)
        self.keyComboBox.setDisabled(True)
        self.styleComboBox.setDisabled(True)
        self.spinBox2.setDisabled(True)
        self.radioButton1.setDisabled(True)
    def Enable_All(self):
        self.spinBox_slavid.setEnabled(True)
        self.spinBox1.setEnabled(True)
        self.comportbutton.setEnabled(True)
        self.keyComboBox.setEnabled(True)
        self.styleComboBox.setEnabled(True)
        self.spinBox2.setEnabled(True)
        self.radioButton1.setEnabled(True)
    def start_auto_refresh(self):
        self.counter=0
        self.timer.start(self.spinBox2.value())
        self.Disable_All()
        self.defaultPushButton.setText("Stop")
        self.defaultPushButton.clicked.disconnect()
        self.defaultPushButton.clicked.connect(self.stop_auto_refresh)
    def stop_auto_refresh(self):
        self.timer.killTimer(self.timer.timerId())
        self.Enable_All()
        self.defaultPushButton.setText("Start")
        self.defaultPushButton.clicked.disconnect()
        self.defaultPushButton.clicked.connect(self.start_auto_refresh)
    def auto_refresh(self):
        if(self.radioButton1.isChecked()):
            self.spinBox2.setEnabled(True)
            self.defaultPushButton.setText("Start")
            self.defaultPushButton.setDefault(True)
            self.defaultPushButton.clicked.disconnect()
            self.defaultPushButton.clicked.connect(self.start_auto_refresh)
        else:
            self.spinBox2.setDisabled(True)
            self.defaultPushButton.setText("Refresh")
            self.defaultPushButton.setDefault(True)
            self.defaultPushButton.clicked.disconnect()
            self.defaultPushButton.clicked.connect(self.refresh_data)
    def createRightBox(self):
        self.RightGroupBox = QGroupBox()
        lable_slavid=QLabel("Slave ID  ")
        self.spinBox_slavid = QSpinBox()
        self.spinBox_slavid.setRange(1,255)
        self.spinBox_slavid.setValue(1)
        lable1=QLabel("Read Timeout (ms) ")
        self.spinBox1 = QSpinBox()
        self.spinBox1.setRange(1,3000)
        self.spinBox1.setValue(100)

        lable3=QLabel("Read Key ")
        self.keyComboBox = QComboBox()
        self.keyComboBox.addItem("big")
        self.keyComboBox.addItem("little")
        # self.keyComboBox.addItem("2301")
        # self.keyComboBox.addItem("3210")
        self.keyComboBox.setCurrentIndex(0)

        lable31=QLabel("Float Reverse")
        self.floatReverseComboBox = QComboBox()
        self.floatReverseComboBox.addItem("False")
        self.floatReverseComboBox.addItem("True")
        # self.keyComboBox.addItem("2301")
        # self.keyComboBox.addItem("3210")
        self.floatReverseComboBox.setCurrentIndex(0)
        self.radioButton1 = QRadioButton("Auto Refresh")
        self.radioButton1.toggled.connect(self.auto_refresh)
        self.lable2=QLabel("Loop Time (ms) ")
        #self.lable2.hide()
        self.spinBox2 = QSpinBox()
        self.spinBox2.setRange(1,20000)
        self.spinBox2.setValue(3000)
        self.spinBox2.setDisabled(True)
        #self.spinBox2.hide()

        self.defaultPushButton = QPushButton("Refresh")
        self.defaultPushButton.setDefault(True)
        self.defaultPushButton.clicked.connect(self.refresh_data)

        self.Error=QLabel()
        self.Error.setStyleSheet('color: red')

        layout = QVBoxLayout()
        layout.addWidget(lable_slavid)
        layout.addWidget(self.spinBox_slavid)
        layout.addWidget(lable1)
        layout.addWidget(self.spinBox1)
        layout.addWidget(lable3)
        layout.addWidget(self.keyComboBox)
        layout.addWidget(lable31)
        layout.addWidget(self.floatReverseComboBox)
        layout.addWidget(QLabel())
        layout.addWidget(QLabel())
        layout.addWidget(QLabel())
        layout.addWidget(QLabel())
        layout.addWidget(QLabel())
        layout.addWidget(QLabel())
        layout.addWidget(QLabel())
        layout.addWidget(QLabel())
        layout.addWidget(self.radioButton1)
        layout.addWidget(self.lable2)
        layout.addWidget(self.spinBox2)
        layout.addWidget(self.defaultPushButton)
        layout.addWidget(self.Error)
        layout.addStretch(1)
        self.RightGroupBox.setLayout(layout)

    def createLeftTabWidget(self):
        self.tableWidget = QTableWidget(20, 5)
        self.tableWidget.setHorizontalHeaderLabels(["Name","Value","Address","RegCount","Type"])
        self.tableWidget.setWindowTitle("Parameters")



if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    # gallery.setFixedSize(gallery.baseSize())
    # gallery.setFixedWidth(600)
    gallery.show()
    sys.exit(app.exec())