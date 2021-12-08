#
# -*- coding: utf-8 -*-
#

import sys
import base64
import os.path
import math
import pathlib
from pathlib import Path
from pprint import pprint 
from playsound import playsound
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QMessageBox, QFileDialog, QLabel, QLCDNumber, QInputDialog, QAbstractItemView, QTableWidgetItem)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import pymysql.cursors
from managerUI import Ui_MainWindow  # импорт нашего сгенерированного ф
import orderUI as orui
from viewDopUI import Ui_ViewWindow
import mysqlUser
import datetime
import searchScript as sc
import filmScript as fc
from viewDopScript import orderClass
import saveDialog as sd
import saveDialogRaschet as sdr

class mywindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super(mywindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Менеджер")
        self.searchWindow = None
        self.werehouse = None
        self.connect()
        self.set_programm_data()
        self.selectManagers()
        self.selectDostavka()
        self.viewRaschet()
        self.ui.loginButton.clicked.connect(self.if_login)
        self.ui.loginButton.clicked.connect(self.selectAllListR)
        self.ui.loginButton.setAutoDefault(True)
        self.ui.passManager.returnPressed.connect(self.ui.loginButton.click)
        self.ui.listR.cellClicked.connect(self.selectItemRaschet)
        self.ui.listR.cellClicked.connect(self.selectAllraschetList)

        self.selectClient()
        self.ui.clientList.cellClicked.connect(self.selectItemClient)

        self.ui.editClient.clicked.connect(self.editClient)
        
        #Кнопка создать клиента
        self.ui.createClient.clicked.connect(self.addClient)
        self.ui.createClient.clicked.connect(self.set_programm_data) #Перечитать данные
        self.ui.createClient.clicked.connect(self.selectClient)
        self.ui.createClient.clicked.connect(self.if_login)
        self.ui.keepClient.clicked.connect(self.keepClient)

        self.ui.createRaschet.clicked.connect(self.createRaschet)
        self.ui.createRaschet.clicked.connect(self.selectAllListR)
        self.ui.createRaschet.clicked.connect(self.selectAllraschetListFromCreate)
        self.ui.updateRaschet.clicked.connect(self.UpdateRaschet)
        self.ui.updateRaschet.clicked.connect(self.selectAllraschetListFromCreate)
        self.ui.updateRaschet.setToolTip("Соханите \n измененные вами данные")
        self.ui.delRow.clicked.connect(self.DelRaschet)
        self.ui.raschetList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.ui.createRaschet.clicked.connect(lambda: self.ui.listR.selectRow(self.ui.listR.rowCount()-1))
        self.ui.addMatR.clicked.connect(self.addMatR)
        self.ui.addMatR.clicked.connect(self.selectAllraschetListFromCreate)
        self.ui.addArmR.clicked.connect(self.addArmR)
        self.ui.addArmR.clicked.connect(self.selectAllraschetListFromCreate)
        self.ui.gotoClient.clicked.connect(self.ui.clientName.setFocus)
        self.ui.gotoClient.clicked.connect(lambda: self.ui.tabWidget.setCurrentIndex(1))
        self.ui.listR.doubleClicked.connect(self.ui.raschetList.setFocus)
        self.ui.listR.doubleClicked.connect(lambda: self.ui.tabWidget.setCurrentIndex(1))
        self.ui.listR.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.gotoR.clicked.connect(lambda: self.ui.tabWidget.setCurrentIndex(1))
        self.selectMaterialColor()
        self.selectMaterialDepth()
        self.selectMaterialMaterial()
        
        self.selectArmColorColor()
        self.ui.selectColor.currentTextChanged.connect(self.selectMaterialMaterial)
        self.ui.colorArm.currentTextChanged.connect(self.selectArmColor)
        self.ui.selectDepth.currentTextChanged.connect(self.selectMaterialMaterial)
        self.ui.createZ.clicked.connect(self.selectDopMatData)
        self.ui.createZ.clicked.connect(self.saveDialog)
        self.ui.createR.clicked.connect(self.selectDopMatData)
        self.ui.createR.clicked.connect(self.saveDialogR)
        #кнопка вызова окна поика клиентов
        self.ui.searchClient.clicked.connect(self.searchClient)
        #кнопка вызова окна "Пленка"
        self.ui.filmButton.clicked.connect(self.werehouseFilm)
        self.ui.filmButton.setToolTip("Откройте, \n чтоб добавить доп.материал")
        self.raschetID = 0
        self.oldManagerName = 0

    #Проверка создан ли конфиг, с настройками подключения к БД
    def connect(self):
        if os.path.isfile("./dbs.conf") is True:
            self.listToCfg = list()
            f = open('dbs.conf')
            for line in f:
                self.listToCfg.append(line.rstrip())
            return self.listToCfg
        else:
            QMessageBox.critical(self, 'Ошибка', "Конфиг не найден соединение не возможно", QMessageBox.Ok)                
    
    #Вытаскиваем все данные из БД(т.е. абсолютно все)
    def set_programm_data(self):
        self.programm_data = dict()
        list_sql_tables = list()
        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
        sql = "show tables"
        list_tables = mysqlUser.query_mysql(cur, sql)    
        for i in list(list_tables._rows):
            list_sql_tables.append(i['Tables_in_vdsi_final'])
            
        for i in list_sql_tables:
            sql = "select * from " + i
            sql_data = mysqlUser.query_mysql(cur, sql)
            self.programm_data[i] = sql_data._rows
        return self.programm_data
    
    #Больше не требуется подключения к бд
    def selectManagers(self):
        for name in self.programm_data['managers']:
            self.ui.selectManager.addItem(name['name'])
    
    #Так же передал в обоход sql
    def if_login(self):
        for i in range(len(self.programm_data['managers'])):
            #Достаем пароль текущего менеджера и опять же без sql
            if self.programm_data['managers'][i]['name'] == self.ui.selectManager.currentText():
                self.programm_data['current_manager_list_id'] = i
                for name in self.programm_data['managers'][i]:
                    self.programm_data['current_manager_' + name] = self.programm_data['managers'][i][name]

        if self.programm_data['managers'][self.programm_data['current_manager_list_id']]['password'] == self.ui.passManager.text():
            
            print("Авторизация пройдена")
            self.ui.gotoClient.setEnabled(True)
            self.ui.gotoR.setEnabled(True)
            self.ui.searchClient.setEnabled(True)
            self.ui.listR.setEnabled(True)
            self.ui.clientName.setEnabled(True)
            self.ui.clientTel.setEnabled(True)
            self.ui.clientMail.setEnabled(True)
            self.ui.clientAddress.setEnabled(True)
            self.ui.selectDost.setEnabled(True)
            self.ui.createClient.setEnabled(True)
            self.ui.editClient.setEnabled(True)
            self.ui.keepClient.setEnabled(True)
            self.ui.clientList.setEnabled(True)
            self.ui.selectColor.setEnabled(True)
            self.ui.selectDepth.setEnabled(True)
            self.ui.selectMaterial.setEnabled(True)
            self.ui.createRaschet.setEnabled(True)
            self.ui.countMaterial.setEnabled(True)
            self.ui.heightMaterial.setEnabled(True)
            self.ui.minPrice.setEnabled(True)
            self.ui.addMatR.setEnabled(True)
            self.ui.nameArm.setEnabled(True)
            self.ui.sizeArm.setEnabled(True)
            self.ui.countArm.setEnabled(True)
            self.ui.heightArm.setEnabled(True)
            self.ui.minPriceArm.setEnabled(True)
            self.ui.minPrice.setEnabled(True)
            self.ui.addArmR.setEnabled(True)
            self.ui.colorArm.setEnabled(True)
            self.ui.raschetList.setEnabled(True)
            self.ui.createR.setEnabled(True)
            self.ui.createZ.setEnabled(True)
            self.ui.updateRaschet.setEnabled(True)
            self.ui.selectManager.setEnabled(False)
            self.ui.passManager.setEnabled(False)
            self.ui.loginButton.setEnabled(False)
            self.ui.delRow.setEnabled(True)
            self.ui.filmButton.setEnabled(True)
            #ТАБ Расчеты
            self.ui.raschetWiewClientList.setEnabled(True)

        else:
            QMessageBox.critical(self, 'Ошибка', "Неверно введен пароль", QMessageBox.Ok)
            self.ui.passManager.setText("")


    # Создать расчет
    def createRaschet(self):

        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
      
      
        sqlManagerID = "select id from managers where name = '"+ self.ui.selectManager.currentText() +"'"
        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
        managerTable = mysqlUser.query_mysql(cur, sqlManagerID)
        for row in managerTable:
            managerID = row["id"]

        sqlClientID = "select id from clients where name = '" + self.oldDataClient + "'"
        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
        clientTable = mysqlUser.query_mysql(cur, sqlClientID)
        for row in clientTable:
            clientID = row["id"]
        sqlDostavkaID = "select id from dostavka where name = '" + self.ui.selectDost.currentText() + "'"
        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
        dostavkaTable = mysqlUser.query_mysql(cur, sqlDostavkaID)
        for row in dostavkaTable:
            dostavkaID = row["id"]
        now = datetime.datetime.now()
        nowDate = now.strftime("%H:%M %d-%m-%Y")
        sql = "insert into raschet set `manager_id` = %d, `client_id` = %d, `date` = '%s', `dostavka_id` = %d" % (managerID, clientID, str(nowDate), dostavkaID)
        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
        mysqlUser.query_mysql(cur, sql)

        sqlRaschetID = "select id from raschet where `date` = '%s'" % (str(nowDate))
        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
        raschetTable = mysqlUser.query_mysql(cur, sqlRaschetID)
        for row in raschetTable:
            raschetID = row["id"]
        self.raschetID = raschetID
        QMessageBox.information(self, 'Готово!', "Расчет успешно создан", QMessageBox.Ok)
        self.oldManagerName = 0
        return self.raschetID
        #файл для чтения в сторонних окнах

    print("Вход в функции апдейт")

    # Поиск клиента
    def searchClient(self):  # поиск клиента

        self.searchWindowClient = sc.searchWindow()
        self.searchWindowClient.show()

    # Добавление в расчет доп.материалов
    def werehouseFilm(self):
        self.allRaschetId = self.oldManagerName + self.raschetID
        # Передаю переменную в окно доп.материалов
        print(self.allRaschetId)
        fc.werehouse.allRaschetId = self.allRaschetId

        self.werehouseFilmWindow = fc.werehouse()
        self.werehouseFilmWindow.show()

    # Создать клиента
    def addClient(self):

        print(self.ui.selectManager.currentText())

        clientName = self.ui.clientName.text()
        clientTel = self.ui.clientTel.text()
        clientAddress = self.ui.clientAddress.text()
        clientMail = self.ui.clientMail.text()
        if not clientName or not clientTel or not clientAddress or not clientMail:
            QMessageBox.critical(self, 'Ошибка', "Одно или несколько полей не заполнено", QMessageBox.Ok)
            if not clientName:
                self.ui.clientName.setStyleSheet("QLineEdit { background: rgb(255, 160, 122); }")
            if not clientTel:
                self.ui.clientTel.setStyleSheet("QLineEdit { background: rgb(255, 160, 122); }")
            if not clientAddress:
                self.ui.clientAddress.setStyleSheet("QLineEdit { background: rgb(255, 160, 122); }")
            if not clientMail:
                self.ui.clientMail.setStyleSheet("QLineEdit { background: rgb(255, 160, 122); }")
        else:
            sql = "insert into clients set `name` = '" + clientName + "',`telephone` = '" + clientTel + "',`address` = '" + clientAddress + "',`mail` = '" + clientMail + "', `manager` = '" + self.ui.selectManager.currentText() + "'"
            cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
            mysqlUser.query_mysql(cur, sql)
            self.ui.clientName.setText("")
            self.ui.clientTel.setText("")
            self.ui.clientAddress.setText("")
            self.ui.clientMail.setText("")
            cur.close()

    # Редактироване данных о клиенте(выбор)
    def editClient(self):
        sqlClientID = "select id from clients where name = '" + self.oldDataClient + "'"
        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
        clientTable = mysqlUser.query_mysql(cur, sqlClientID)
        for row in clientTable:
            clientID = row["id"]
        sqlSelectAllDataClient = "select * from `clients` where id = '%s'" % (clientID)
        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
        DataClientTable = mysqlUser.query_mysql(cur, sqlSelectAllDataClient)
        for row in DataClientTable:
            clientName = row["name"]
            clientTelephone = row["telephone"]
            clientEmail = row["mail"]
            clientAddress = row["address"]

        self.ui.clientName.setText(f"{clientName}")
        self.ui.clientTel.setText(f"{clientTelephone}")
        self.ui.clientAddress.setText(f"{clientEmail}")
        self.ui.clientMail.setText(f"{clientAddress}")

    # Редактироване данных о клиенте(сохранение в БД)
    def keepClient(self):

        clientName = self.ui.clientName.text()
        clientTel = self.ui.clientTel.text()
        clientAddress = self.ui.clientAddress.text()
        clientMail = self.ui.clientMail.text()
        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])

        print(clientName, clientTel, clientAddress, clientMail)

        sqlClientID = "select id from clients where name = '" + self.oldDataClient + "'"
        clientTable = mysqlUser.query_mysql(cur, sqlClientID)
        for row in clientTable:
            clientID = row["id"]

        sqlUpdateClient = "update clients set `name` = '%s', `telephone` = '%s', `mail` = '%s', `address` = '%s' where `id` = '%s'" % (clientName, clientTel, clientAddress, clientMail, clientID)
        mysqlUser.query_mysql(cur, sqlUpdateClient)

        self.ui.clientName.setText("")
        self.ui.clientTel.setText("")
        self.ui.clientAddress.setText("")
        self.ui.clientMail.setText("")
        
        QMessageBox.information(self, 'Готово', "Изменения внесены успешко", QMessageBox.Ok)
        cur.close()

    # Избавились от sql
    def selectDostavka(self):
        for name in self.programm_data['dostavka']:
            self.ui.selectDost.addItem(name['name'])

    # Избавились от sql
    def selectClient(self):
        self.ui.clientList.setRowCount(0)
        for client in self.programm_data['clients']:
            a = self.ui.clientList.rowCount()
            self.ui.clientList.setRowCount(self.ui.clientList.rowCount()+1)
            self.ui.clientList.setItem(a, 0, QtWidgets.QTableWidgetItem(client["name"]))
            self.ui.clientList.setItem(a, 1, QtWidgets.QTableWidgetItem(str(client["telephone"])))

    # Так же избавились от sql
    def selectMaterialColor(self):
        for color in self.programm_data['color']:
            self.ui.selectColor.addItem(color['name'])

    # Избавились от sql
    def selectMaterialDepth(self): # Избавились от sql
        for depth in self.programm_data['depth']:
            self.ui.selectDepth.addItem(depth['name'])

    # Избавились от sql
    def selectArmColorColor(self):
        for ArmColor in self.programm_data['color']:
            self.ui.colorArm.addItem(ArmColor['name'])
    
    # Избавились от sql
    def selectMaterialMaterial(self):

        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])

        sqlColorID = "select id from color where name = '"+ self.ui.selectColor.currentText() +"'"
        colorTable = mysqlUser.query_mysql(cur, sqlColorID)
        for row in colorTable:
            colorID = row["id"]
            
        sqlDepthID = "select id from depth where name = '"+ self.ui.selectDepth.currentText() +"'"
        depthTable = mysqlUser.query_mysql(cur, sqlDepthID)
        for row in depthTable:
            depthID = row["id"]
            
        self.ui.selectMaterial.clear()
        sql = "select * from materials where `color_id` = %d and `depth_id` = %d" % (colorID, depthID)
        table_materials = mysqlUser.query_mysql(cur, sql)
        for row in table_materials:
            self.ui.selectMaterial.addItem(row['name'])
        cur.close()

    # Избавились от sql
    def selectArmColor(self):

        sqlArmColorID = "select id from color where name = '"+ self.ui.colorArm.currentText() +"'"
        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
        colorArmTable = mysqlUser.query_mysql(cur, sqlArmColorID)
        for row in colorArmTable:
            colorArmID = row["id"]
        cur.close()

    # Выбрать клиента из виджета
    def selectItemClient(self):
        self.oldDataClient = self.ui.clientList.selectedItems()[0].text()
        print(self.ui.clientList.selectedItems()[0].text())
        return self.oldDataClient

    # Добавить материал
    def addMatR(self):
        print(self.raschetID, self.oldManagerName)
        countMat = self.ui.countMaterial.text()
        heightMat = self.ui.heightMaterial.text()
        priceMat = self.ui.minPrice.text()
        colorMat = self.ui.selectColor.currentText()
        depthMat = self.ui.selectDepth.currentText()


        if not countMat or not heightMat or not priceMat:
            QMessageBox.critical(self, 'Ошибка', "Одно или несколько полей не заполнено", QMessageBox.Ok)
            if not countMat:
                self.ui.countMaterial.setStyleSheet("QLineEdit { background: rgb(255, 160, 122); }")
            if not heightMat:
                self.ui.heightMaterial.setStyleSheet("QLineEdit { background: rgb(255, 160, 122); }")
            if not priceMat:
                self.ui.minPrice.setStyleSheet("QLineEdit { background: rgb(255, 160, 122); }")
        else:
            cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
            raschetID = self.raschetID + self.oldManagerName

            sqlMatID = "select id from materials where `name` = '%s'" % (self.ui.selectMaterial.currentText())
            matTable = mysqlUser.query_mysql(cur, sqlMatID)
            for row in matTable:
                matID = row['id']

            sqlColID = "select id from color where `name` = '%s'" % (self.ui.selectColor.currentText())
            ColTable = mysqlUser.query_mysql(cur, sqlColID)
            for row in ColTable:
                ColID = row['id']

            sqlDepID = "select id from depth where `name` = '%s'" % (self.ui.selectDepth.currentText())
            DepTable = mysqlUser.query_mysql(cur, sqlDepID)
            for row in DepTable:
                DepID = row['id']

            sqlNewMatID = "select id from materials where `name` = '%s' and `color_id` = %d and `depth_id` = %d" % (self.ui.selectMaterial.currentText(), ColID, DepID)
            matNewTable = mysqlUser.query_mysql(cur, sqlNewMatID)
            for row in matNewTable:
                matNewID = row['id']

            print("matNewID:", matNewID, "\n", "ColID:", ColID, "\n", "DepID:", DepID) 

            sqlPriceMat = f"select min_price from materials where `id` = {matNewID}"
            PriceTable = mysqlUser.query_mysql(cur, sqlPriceMat)
            for rows in PriceTable:
                priceId = rows['min_price']
            print(priceId)
            print(self.ui.minPrice.text())
            PriceFromLine = float(self.ui.minPrice.text())
            if PriceFromLine < priceId:
                QMessageBox.critical(self, 'Ошибка', "Вы не можете ставить цену ниже минимальной\nЧитайте инструкцию", QMessageBox.Ok)
            elif PriceFromLine == priceId:
                QMessageBox.critical(self, 'Внимание!', "Цена предельно допустима\nЧитайте инструкцию", QMessageBox.Ok)
                sqlAddMatR = "insert into items_to_raschet set `raschet_id` = '" + Raschet + "', `material_id` = '" + matName + "',`count` = '" + countMat + "',`height` = '" + heightMat + "',`price` = '" + priceMat + "',`color_id` = '" + colorMat + "', `depth_id` = '" + depthMat + "'"
                mysqlUser.query_mysql(cur, sqlAddMatR)
            else:
                Raschet = str(raschetID)
                matName = str(matID)
                sqlAddMatR = "insert into items_to_raschet set `raschet_id` = '" + Raschet + "', `material_id` = '" + matName + "',`count` = '" + countMat + "',`height` = '" + heightMat + "',`price` = '" + priceMat + "',`color_id` = '" + colorMat + "', `depth_id` = '" + depthMat + "'"
                mysqlUser.query_mysql(cur, sqlAddMatR)

            self.ui.countMaterial.setStyleSheet("QLineEdit { background: rgb(255, 255, 255); }")
            self.ui.heightMaterial.setStyleSheet("QLineEdit { background: rgb(255, 255, 255); }")
            self.ui.minPrice.setStyleSheet("QLineEdit { background: rgb(255, 255, 255); }")

            cur.close()
    
    def addArmR(self):

        raschetID = self.raschetID + self.oldManagerName

        DoborName = self.ui.nameArm.text()
        DoborColor = self.ui.colorArm.currentText()
        DoborSize = self.ui.sizeArm.text()
        DoborCount = self.ui.countArm.text()
        DoborHeight = self.ui.heightArm.text()
        DoborPrice = self.ui.minPriceArm.text()
        raschet = str(raschetID)

        if not DoborName or not DoborSize or not DoborCount or not DoborHeight or not DoborPrice:
            QMessageBox.critical(self, 'Ошибка', "Одно или несколько полей не заполнено", QMessageBox.Ok)
            if not DoborName:
                self.ui.nameArm.setStyleSheet("QLineEdit { background: rgb(255, 160, 122); }")
            if not DoborSize:
                self.ui.sizeArm.setStyleSheet("QLineEdit { background: rgb(255, 160, 122); }")
            if not DoborCount:
                self.ui.countArm.setStyleSheet("QLineEdit { background: rgb(255, 160, 122); }")
            if not DoborHeight:
                self.ui.heightArm.setStyleSheet("QLineEdit { background: rgb(255, 160, 122); }")
            if not DoborPrice:
                self.ui.minPriceArm.setStyleSheet("QLineEdit { background: rgb(255, 160, 122); }")
        else:        

            print("Название:", DoborName, "\n", "Цвет:", DoborColor, "\n", "Развертка:", DoborSize, "\n", "Количество:", DoborCount, "\n", "Длина:", DoborHeight, "\n", "Цена:", DoborPrice, "\n", "Расчет:", raschet)

            sqlAddArmR = "insert into items_to_raschet set `raschet_id` = '" + raschet + "', `name_Arm` = '" + DoborName + "',`count` = '" + DoborCount + "',`size_Arm` = '" + DoborSize + "',`height` = '" + DoborHeight + "',`price` = '" + DoborPrice + "', `color_id` = '" + DoborColor + "'"
            cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
            mysqlUser.query_mysql(cur, sqlAddArmR)

            self.ui.nameArm.setStyleSheet("QLineEdit { background: rgb(255, 255, 255); }")
            self.ui.sizeArm.setStyleSheet("QLineEdit { background: rgb(255, 255, 255); }")
            self.ui.countArm.setStyleSheet("QLineEdit { background: rgb(255, 255, 255); }")
            self.ui.heightArm.setStyleSheet("QLineEdit { background: rgb(255, 255, 255); }")
            self.ui.minPriceArm.setStyleSheet("QLineEdit { background: rgb(255, 255, 255); }")

            cur.close()

#    def selectRList(self):
#        self.ui.raschetList.setRowCount(0)
#        sqlRaschetList = "select * form items_to_raschet where `raschet_id` = %s" % (self.raschetID)
#        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
#        tableListR = mysqlUser.query_mysql(cur, sqlRaschetList)
        
#        for row in tableListR: 
#            a = self.ui.raschetList.rowCount()
#            self.ui.raschetList.setRowCount(self.ui.listR.rowCount() + 1)
#            self.ui.raschetList.setItem(a, 0, QtWidgets.QTableWidgetItem(row["date"]))
#            self.ui.raschetList.setItem(a, 1, QtWidgets.QTableWidgetItem(row["manager_id"]))
#            self.ui.raschetList.setItem(a, 2, QtWidgets.QTableWidgetItem(row["client_id"]))
#            self.ui.raschetList.setItem(a, 3, QtWidgets.QTableWidgetItem(row["dostavka_id"]))
#            self.resultDict = {"raschet_id":row["id"], "date":row["date"], "manager":row["manager_id"], "client":row["client_id"], "dostavka":row["dostavka_id"]}
#        return self.resultDict

    # Отрисовка в виджете главной страницы от имени менеджера
    def selectAllListR(self):
        self.ui.listR.setRowCount(0)
        managerID = self.programm_data['current_manager_id']
        
        sqlListR = "select managers.name as manager_id, clients.name as client_id, raschet.date, dostavka.name as dostavka_id, raschet.id as manID from raschet inner join managers on (managers.id=raschet.manager_id) inner join clients on (clients.id = raschet.client_id) inner join dostavka on (dostavka.id = raschet.dostavka_id) where `manager_id` = %s" % (managerID)
        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
        tableListR = mysqlUser.query_mysql(cur, sqlListR)
        self.manID = list()
        for row in tableListR: 
            a = self.ui.listR.rowCount()
            print(row['manager_id'], row['manID'])
            self.ui.listR.setRowCount(self.ui.listR.rowCount() + 1)
            self.ui.listR.setItem(a, 0, QtWidgets.QTableWidgetItem(row["date"]))
            self.ui.listR.setItem(a, 1, QtWidgets.QTableWidgetItem(row["manager_id"]))
            self.ui.listR.setItem(a, 2, QtWidgets.QTableWidgetItem(row["client_id"]))
            self.ui.listR.setItem(a, 3, QtWidgets.QTableWidgetItem(row["dostavka_id"]))
            self.manID.append(row['manID'])
        return self.manID
        cur.close()

    # Отрисовка материалов уже созданного заказа материалов в виджете стрницы расчет и заказ
    def selectAllraschetList(self):
        print(self.raschetID, self.oldManagerName)
        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
        print(self.oldManagerName, "такая фигня selectAllraschetList")
        # Вставить словарь данных
        materialsData = list()
        armatureData = list()
        self.resultDict = {"date": self.ui.listR.item(self.ui.listR.currentRow(), 0).text(),
                           "manager": self.ui.listR.item(self.ui.listR.currentRow(), 1).text(),
                           "client": self.ui.listR.item(self.ui.listR.currentRow(), 2).text(),
                           "dostavka": self.ui.selectDost.currentText()}
        
        sqlToMaterials = "SELECT items_to_raschet.id, items_to_raschet.raschet_id, materials.name as material_id, items_to_raschet.count, items_to_raschet.height, items_to_raschet.price, items_to_raschet.color_id, items_to_raschet.depth_id, materials.width FROM `items_to_raschet` inner join materials on (materials.id = items_to_raschet.material_id) WHERE raschet_id = %s" % (self.oldManagerName)
        sqlToArmature = "SELECT items_to_raschet.id, items_to_raschet.raschet_id, items_to_raschet.name_Arm, items_to_raschet.count, items_to_raschet.price, items_to_raschet.color_id, items_to_raschet.size_Arm, items_to_raschet.height from `items_to_raschet` WHERE name_Arm is NOT NULL and raschet_id = %s" % (self.oldManagerName)

        toolTipText = "<h1>Материалы:</h1>\n<table border='1'><tr><th>Материал</th><th>Количество</th><th>Длина</th><th>Цена</th><th>Цвет</th><th>Толщина/Развертка</th>\n"
        
        self.ui.raschetList.setRowCount(0)

        tableMaterial = mysqlUser.query_mysql(cur, sqlToMaterials)

        for row in tableMaterial:
            print(row)
            a = self.ui.raschetList.rowCount()
            self.ui.raschetList.setRowCount(a + 1)
            self.ui.raschetList.setItem(a, 0, QtWidgets.QTableWidgetItem(str(row["id"])))
            self.ui.raschetList.setItem(a, 1, QtWidgets.QTableWidgetItem(row["material_id"]))
            self.ui.raschetList.setItem(a, 2, QtWidgets.QTableWidgetItem(row["count"]))
            self.ui.raschetList.setItem(a, 3, QtWidgets.QTableWidgetItem(row["height"]))
            self.ui.raschetList.setItem(a, 4, QtWidgets.QTableWidgetItem(row["price"]))
            self.ui.raschetList.setItem(a, 5, QtWidgets.QTableWidgetItem(row["color_id"]))
            self.ui.raschetList.setItem(a, 6, QtWidgets.QTableWidgetItem(row["depth_id"]))
            materialsData.append(row)
            toolTipText +=  "<tr><td>" + row["material_id"] + '</td><td>' + row["count"] + '</td><td>' + row[
                "height"] + '</td><td>' + row["price"] + '</td><td>' + row["color_id"] + '</td><td>' + row[
                            "depth_id"] + '</td><td>\n'

        tableArmature = mysqlUser.query_mysql(cur, sqlToArmature)

        for row in tableArmature:
            print(row)
            a = self.ui.raschetList.rowCount()
            self.ui.raschetList.setRowCount(a + 1)
            self.ui.raschetList.setItem(a, 0, QtWidgets.QTableWidgetItem(str(row["id"])))
            self.ui.raschetList.setItem(a, 1, QtWidgets.QTableWidgetItem(row["name_Arm"]))
            self.ui.raschetList.setItem(a, 2, QtWidgets.QTableWidgetItem(row["count"]))
            self.ui.raschetList.setItem(a, 3, QtWidgets.QTableWidgetItem(row["height"]))
            self.ui.raschetList.setItem(a, 4, QtWidgets.QTableWidgetItem(row["price"]))
            self.ui.raschetList.setItem(a, 5, QtWidgets.QTableWidgetItem(row["color_id"]))
            self.ui.raschetList.setItem(a, 7, QtWidgets.QTableWidgetItem(row["size_Arm"]))
            armatureData.append(row)
            toolTipText += "<tr><td>" + row["name_Arm"] + '</td><td>' + row["count"] + '</td><td>' + row[
                "height"] + '</td><td>' + row["price"] + '</td><td>' + row["color_id"] + '</td><td>' + row[
                                    "size_Arm"] + '</td></tr>\n'
        toolTipText += "</table>"
        self.stringToQr = "Сформировано в ее ВДСИ\nДата:{date}\nМенеджер:{manager}\nЗаказчик:{client}".format(date=self.ui.listR.item(self.ui.listR.currentRow(), 0).text(), manager=self.ui.listR.item(self.ui.listR.currentRow(), 1).text(), client=self.ui.listR.item(self.ui.listR.currentRow(), 2).text())

        self.ui.listR.item(self.ui.listR.currentRow(), 0).setToolTip(toolTipText)
        self.ui.listR.item(self.ui.listR.currentRow(), 1).setToolTip(toolTipText)
        self.ui.listR.item(self.ui.listR.currentRow(), 2).setToolTip(toolTipText)
        self.ui.listR.item(self.ui.listR.currentRow(), 3).setToolTip(toolTipText)

	

        self.resultDict['materials'] = materialsData
        self.resultDict['product'] = self.manID
        self.resultDict['armatures'] = armatureData
        self.resultDict['string_to_qr'] = self.stringToQr
        return self.resultDict
        cur.close()

    # Отрисовка добовляемых материалов в виджете стрницы расчет и заказ
    def selectAllraschetListFromCreate(self):
        print(self.raschetID, self.oldManagerName)
        raschetID = self.raschetID + self.oldManagerName
        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])

        print(raschetID , "такая фигня  selectAllraschetListFromCreate")
        self.ui.raschetList.setRowCount(0)

        sqlToMaterials = "SELECT items_to_raschet.id, items_to_raschet.raschet_id, materials.name as material_id, items_to_raschet.count, items_to_raschet.height, items_to_raschet.price, items_to_raschet.color_id, items_to_raschet.depth_id, materials.width FROM `items_to_raschet` inner join materials on (materials.id = items_to_raschet.material_id) WHERE material_id is NOT NULL and raschet_id = %s" % (raschetID)
        tableMaterial = mysqlUser.query_mysql(cur, sqlToMaterials)
        for row in tableMaterial:
            print(row)
            a = self.ui.raschetList.rowCount()
            self.ui.raschetList.setRowCount(self.ui.raschetList.rowCount() + 1)
            self.ui.raschetList.setItem(a, 0, QtWidgets.QTableWidgetItem(str(row["id"])))
            self.ui.raschetList.setItem(a, 1, QtWidgets.QTableWidgetItem(row["material_id"]))
            self.ui.raschetList.setItem(a, 2, QtWidgets.QTableWidgetItem(row["count"]))
            self.ui.raschetList.setItem(a, 3, QtWidgets.QTableWidgetItem(row["height"]))
            self.ui.raschetList.setItem(a, 4, QtWidgets.QTableWidgetItem(row["price"]))
            self.ui.raschetList.setItem(a, 5, QtWidgets.QTableWidgetItem(row["color_id"]))
            self.ui.raschetList.setItem(a, 6, QtWidgets.QTableWidgetItem(row["depth_id"]))
        
        sqlToArmature = "SELECT items_to_raschet.id, items_to_raschet.raschet_id, items_to_raschet.name_Arm, items_to_raschet.count, items_to_raschet.price, items_to_raschet.color_id, items_to_raschet.size_Arm, items_to_raschet.height FROM items_to_raschet WHERE name_Arm is NOT NULL and raschet_id = %s" % (raschetID)
        tableArmature = mysqlUser.query_mysql(cur, sqlToArmature)
        for row in tableArmature:
            a = self.ui.raschetList.rowCount()
            self.ui.raschetList.setRowCount(a + 1)
            self.ui.raschetList.setItem(a, 0, QtWidgets.QTableWidgetItem(str(row["id"])))
            self.ui.raschetList.setItem(a, 1, QtWidgets.QTableWidgetItem(row["name_Arm"]))
            self.ui.raschetList.setItem(a, 2, QtWidgets.QTableWidgetItem(row["count"]))
            self.ui.raschetList.setItem(a, 3, QtWidgets.QTableWidgetItem(row["height"]))
            self.ui.raschetList.setItem(a, 4, QtWidgets.QTableWidgetItem(row["price"]))
            self.ui.raschetList.setItem(a, 5, QtWidgets.QTableWidgetItem(row["color_id"]))
            self.ui.raschetList.setItem(a, 7, QtWidgets.QTableWidgetItem(row["size_Arm"]))
        cur.close()
    # Обновить расчет

    def UpdateRaschet(self):
        
        raschetID = self.raschetID + self.oldManagerName
        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])

        index_row = []
        for i in self.ui.raschetList.selectedIndexes():
            index_row.append(i.row())
        print(index_row)

        row = self.ui.raschetList.currentIndex().row()
        col = self.ui.raschetList.currentIndex().column()
        print("row={}, col={}".format(row, col))

        print("текущая строка ->{}".format(self.ui.raschetList.model().data(self.ui.raschetList.currentIndex())))
        print("первый столбец ->{}".format(self.ui.raschetList.model().index(row, 0).data()))

        idRas = format(self.ui.raschetList.model().index(row, 0).data())

        name = format(self.ui.raschetList.model().index(row, 1).data())
        count = format(self.ui.raschetList.model().index(row, 2).data())
        height = format(self.ui.raschetList.model().index(row, 3).data())
        price = format(self.ui.raschetList.model().index(row, 4).data())
        color = format(self.ui.raschetList.model().index(row, 5).data())
        depth = format(self.ui.raschetList.model().index(row, 6).data())
        rasvertka = format(self.ui.raschetList.model().index(row, 7).data())

        c = self.ui.raschetList.model().data(self.ui.raschetList.currentIndex())
        t = self.ui.raschetList.selectedIndexes()
        leoList = []
        for i in t:
            leoList.append(i.data())
        print(leoList)
        if leoList[-1] != None:

            colorList = []
            color_name = ""

            sqlSelectColorArm = "SELECT `name` FROM `color`"
            tableColor = mysqlUser.query_mysql(cur, sqlSelectColorArm)
            for row in tableColor:
                colorList.append(row)
            for x in colorList:
                col_name = x.get('name')
                if color == col_name:
                    color_name = col_name
            print("color_name: ", color_name)


            colorList.clear()

            if color_name != "":
                updateArm = "UPDATE items_to_raschet SET `name_Arm` = '%s', `size_Arm` = '%s', `count` = '%s', `color_id` = '%s', `height` = '%s', `price` = '%s' WHERE `raschet_id` = %d AND `id` = '%s'" % (name, rasvertka, count, color, height, price, raschetID, idRas)
                print(updateArm)
                mysqlUser.query_mysql(cur, updateArm)
                QMessageBox.information(self, 'Успешно', "Изменения сохранены!", QMessageBox.Ok)
            else:
                QMessageBox.critical(self, 'Ошибка', "В базе нет такого цвета!", QMessageBox.Ok)
        else:

            colorList = []
            color_name = ""
            
            sqlSelectColor = "SELECT `name` FROM `color`"
            tableColor = mysqlUser.query_mysql(cur, sqlSelectColor)
            for row in tableColor:
                colorList.append(row)
            for x in colorList:
                col_name = x.get('name')
                if color == col_name:
                    color_name = col_name
            print("color_name: ", color_name)
            colorList.clear()

            depthList = []
            depth_name = ""

            sqlSelectDepth = "SELECT `name` FROM `depth`"
            tableDepth = mysqlUser.query_mysql(cur, sqlSelectDepth)
            for row in tableDepth:
                depthList.append(row)
            for x in depthList:
                dep_name = x.get('name')
                if depth == dep_name:
                    depth_name = dep_name
            print("depth_name: ", depth_name)
            depthList.clear()

            matList = []
            mat_name = ""

            sqlSelectMat = "SELECT `name` FROM `materials`"
            tableMat = mysqlUser.query_mysql(cur, sqlSelectMat)
            for row in tableMat:
                matList.append(row)
            for x in matList:
                m_name = x.get('name')
                if name == m_name:
                    mat_name = m_name
            print("mat_name: ", mat_name)
            matList.clear()
            
            if color_name == "":
                QMessageBox.critical(self, 'Ошибка', "Не изменено! \n В базе нет такого цвета", QMessageBox.Ok)

            if depth_name == "":
                QMessageBox.critical(self, 'Ошибка', "Не изменено! \n В базе нет такой толщины", QMessageBox.Ok)

            if mat_name == "":
                QMessageBox.critical(self, 'Ошибка', "Не изменено! \n В базе нет такого материала \n попробуйте написать с маленькой \n или большой буквы! \n или измените раскладку", QMessageBox.Ok)
            else:
                sqlIdColor = "SELECT id FROM color WHERE `name` = '%s'" % (color)
                tableColor = mysqlUser.query_mysql(cur, sqlIdColor)
                for row in tableColor:
                    idColor = row['id']

                sqlIdDepth = "SELECT id FROM depth WHERE `name` = '%s'" % (depth)
                tableDepth = mysqlUser.query_mysql(cur, sqlIdDepth)
                for row in tableDepth:
                    idDepth = row['id']
                
                if mat_name != "":
                    name = mat_name

                IdMaterial = ""
                sqlIdMaterial = "SELECT id FROM materials WHERE `name` = '%s' AND `color_id` = %d AND `depth_id` = %d" % (name, idColor, idDepth)
                materialTable = mysqlUser.query_mysql(cur, sqlIdMaterial)
                for row in materialTable:
                    IdMaterial = row['id']
                print("IdMaterial: ", IdMaterial)
                if IdMaterial == "":
                    QMessageBox.critical(self, 'Ошибка', "Не изменено! \n Для данного материала не существует того цвета \n или толщины, что указаны в таблице, \n попробуйте изменить раскладку", QMessageBox.Ok)

                else:
                    sqlPriceMatUp = "SELECT min_price FROM materials WHERE `id` = %d" % (IdMaterial)
                    priceTable = mysqlUser.query_mysql(cur, sqlPriceMatUp)
                    for row in priceTable:
                        priceID = row['min_price']

                    priceFromLine = float(price)
                    if priceFromLine < priceID:
                        QMessageBox.critical(self, 'Ошибка!', "Вы не можете ставить цену ниже минимальной\nЧитайте инструкцию", QMessageBox.Ok)
                    elif priceFromLine == priceID:
                        QMessageBox.critical(self, 'Внимание!', "Цена предельно допустима\nЧитайте инструкцию", QMessageBox.Ok)

                        update = "UPDATE items_to_raschet SET `material_id` = '%s', `count` = '%s', `color_id` = '%s', `depth_id` = '%s', `height` = '%s', `price` = '%s' WHERE `raschet_id` = '%s' AND `id` = '%s'" % (IdMaterial, count, color, depth, height, price, raschetID, idRas)
                        print(update)
                        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
                        mysqlUser.query_mysql(cur, update)
                        QMessageBox.information(self, 'Успешно!', "Изменения сохранены!", QMessageBox.Ok)
                    else:
                        update = "UPDATE items_to_raschet SET `material_id` = '%s', `count` = '%s', `color_id` = '%s', `depth_id` = '%s', `height` = '%s', `price` = '%s' WHERE `raschet_id` = '%s' AND `id` = '%s'" % (IdMaterial, count, color, depth, height, price, raschetID, idRas)
                        print(update)
                        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
                        mysqlUser.query_mysql(cur, update)
                        QMessageBox.information(self, 'Успешно!', "Изменения сохранены!", QMessageBox.Ok)

        leoList.clear()
        cur.close()
    # Удаление строки расчета
    def DelRaschet(self):

        index_row = []
        for i in self.ui.raschetList.selectedIndexes():
            index_row.append(i.row())

        row = self.ui.raschetList.currentIndex().row()
        col = self.ui.raschetList.currentIndex().column()

        print("row={}, col={}".format(row, col))

        print("текущая строка ->{}".format(self.ui.raschetList.model().data(self.ui.raschetList.currentIndex())))
        print("первый столбец ->{}".format(self.ui.raschetList.model().index(row, 0).data()))

        IDRas = format(self.ui.raschetList.model().index(row, 0).data())

        index_row = list(set(index_row))
        for item in index_row:
            self.ui.raschetList.removeRow(item)
        print(index_row)
        index = index_row[0]
        t = int(index)
        print(t)

        c = self.ui.raschetList.selectionModel().selectedRows()

        SqlDelRows = f"delete from items_to_raschet where `id` = {IDRas}"
        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
        mysqlUser.query_mysql(cur, SqlDelRows)
        print(SqlDelRows)
        index_row.clear()
        cur.close()

    def viewRaschet(self):

        self.ui.raschetWiewClientList.setRowCount(0)
        order_id = ''
        sqlTreeViewItems = "select orders.id, orders.date, clients.name as client_id, managers.name as manager_id from orders inner join managers on (managers.id=orders.manager_id) inner join clients on (clients.id = orders.client_id)"# where `manager_id` = %s" % (managerID)
        cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
        tableTreeItems = mysqlUser.query_mysql(cur, sqlTreeViewItems)
        for row in tableTreeItems:

            a = self.ui.raschetWiewClientList.rowCount()
            self.ui.raschetWiewClientList.setRowCount(a + 1)
            self.ui.raschetWiewClientList.setItem(a, 0, QtWidgets.QTableWidgetItem(str(row["id"])))
            self.ui.raschetWiewClientList.setItem(a, 1, QtWidgets.QTableWidgetItem(row["date"]))
            self.ui.raschetWiewClientList.setItem(a, 2, QtWidgets.QTableWidgetItem(row["client_id"]))
            self.ui.raschetWiewClientList.setItem(a, 3, QtWidgets.QTableWidgetItem(row["manager_id"]))
            order_id = str(row['id'])


            def viewWar():
            
                row = self.ui.raschetWiewClientList.currentIndex().row()
                col = self.ui.raschetWiewClientList.currentIndex().column()

                print("row={}, col={}".format(row, col))

                print("текущая строка ->{}".format(self.ui.raschetWiewClientList.model().data(self.ui.raschetWiewClientList.currentIndex())))
                print("первый столбец ->{}".format(self.ui.raschetWiewClientList.model().index(row, 0).data()))

                orderID = format(self.ui.raschetWiewClientList.model().index(row, 0).data())
                nameClient = format(self.ui.raschetWiewClientList.model().index(row, 2).data())

                orderClass.nameClient = nameClient
                orderClass.orderID = orderID
                self.orderClass = orderClass()
                self.orderClass.show()
        if order_id != '':
            self.ui.raschetWiewClientList.cellClicked.connect(viewWar)
        cur.close()

    def selectDopMatData(self):

        if self.oldManagerName == 0:
            pass
        else:

            DopMatDataViewWar = list()

            sqlSelectDopMattreeViewWar = "SELECT dop_mat_raschet.raschet_id, armature.name AS mat_name, dop_mat_raschet.count, dop_mat_raschet.color_id, dop_mat_raschet.price, dop_mat_raschet.razdel_id FROM dop_mat_raschet INNER JOIN armature ON (armature.id = dop_mat_raschet.mat_name) WHERE raschet_id = %s" % (self.oldManagerName)
            cur = mysqlUser.con_mysql(self.listToCfg[0], self.listToCfg[1], self.listToCfg[2], self.listToCfg[3])
            tableDopMatViewWar = mysqlUser.query_mysql(cur, sqlSelectDopMattreeViewWar)
            for row in tableDopMatViewWar:
                DopMatDataViewWar.append(row)
            self.resultDict['dop_materials'] = DopMatDataViewWar
            if len(self.resultDict['dop_materials']) != 0:
                print("----------------", "\n", self.resultDict['dop_materials'], "\n", "---------------")
                print(self.resultDict['dop_materials'][0]['mat_name'], "\n", self.resultDict['dop_materials'][0]['count']
                    , "\n", self.resultDict['dop_materials'][0]['price'], "\n", "------------")

    # Перед тем как отрисовать матереиалы ранее добавленные в расчет
    # Необходимо получить айдишник расчета
    def selectItemRaschet(self):
        self.raschetID = 0
        self.oldManagerName = self.manID[self.ui.listR.currentRow()]
        print(self.ui.listR.selectedItems()[0].text(), self.manID[self.ui.listR.currentRow()])
        return self.oldManagerName
        fc.werehouse.oldManagerName = self.oldManagerName


    def saveDialog(self):

        if self.oldManagerName == 0:
            QMessageBox.critical(self, 'Ошибка', "Обновите список!\nНужно перейти на главную страницу\nи выбрать расчет, который\nвы создали.", QMessageBox.Ok)
        else:
            print(self.oldManagerName)
            sd.Savedialog.oldManagerName = self.oldManagerName
            sd.Savedialog.resultDict = self.resultDict
            #print(materialsData)
            sd.Savedialog.resultDictList = self.resultDict['materials']
            sd.Savedialog.resultDictDopMatList = self.resultDict['dop_materials']
            sd.Savedialog.resultDictArmList = self.resultDict['armatures']
            sd.Savedialog.current_manager = self.programm_data['current_manager_id']
            sd.Savedialog.date_create = self.ui.listR.item(self.ui.listR.currentRow(), 0).text()
            sd.Savedialog.dostavka = self.ui.selectDost.currentText()

            self.saveDialogS = sd.Savedialog()

            #self.saveDialogS.show()

    def saveDialogR(self):

        if self.oldManagerName == 0:
            QMessageBox.critical(self, 'Ошибка', "Обновите список!\nНужно перейти на главную страницу\nи выбрать расчет, который\nвы создали.", QMessageBox.Ok)
        else:
            print(self.oldManagerName)
            sdr.SaveDialogR.oldManagerName = self.oldManagerName
            sdr.SaveDialogR.resultDict = self.resultDict
            #print(materialsData)
            sdr.SaveDialogR.resultDictList = self.resultDict['materials']
            sdr.SaveDialogR.resultDictDopMatList = self.resultDict['dop_materials']
            sdr.SaveDialogR.resultDictArmList = self.resultDict['armatures']
            sdr.SaveDialogR.current_manager = self.programm_data['current_manager_id']
            sdr.SaveDialogR.date_create = self.ui.listR.item(self.ui.listR.currentRow(), 0).text()
            sdr.SaveDialogR.dostavka = self.ui.selectDost.currentText()

            self.saveDialogR = sdr.SaveDialogR()
            #self.saveDialogR.show()

                                         
app = QtWidgets.QApplication([])
application = mywindow()
application.show()
sys.exit(app.exec())
