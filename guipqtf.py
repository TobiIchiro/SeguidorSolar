# -*- coding: utf-8 -*-
"""
Created on Fri May 27 14:38:23 2022

@author: yasse
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsDropShadowEffect, QStackedWidget, QMessageBox, QFileDialog
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QColor
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

import serial
import math

import time

import glob

from geopy.geocoders import Nominatim

from datetime import datetime
import pytz 
from time import sleep
today = datetime.now()
filtro=[0,0,0,0,0]
import numpy as np
from numpy import cos as cos
from numpy import sin as sin
from numpy import pi as pi
from numpy import deg2rad as dr
from numpy import rad2deg as rd
from numpy import arctan as atan

try:
    import httplib
except:
    import http.client as httplib
    
import matplotlib
matplotlib.use('Qt5agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super(VentanaPrincipal, self).__init__()
        loadUi('MSTS2GDLMain.ui', self)

        #Figuras plot
        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.lytDirecta.addWidget(self.canvas)
        self.canvas.draw()
        
        self.figure2 = Figure()
        self.ax2 = self.figure2.add_subplot(111)
        self.canvas2 = FigureCanvasQTAgg(self.figure2)
        self.lytGlobal.addWidget(self.canvas2)
        self.canvas2.draw()
        
        self.ax2.axes.set_xlabel("Time (h)")
        self.ax2.axes.set_ylabel("Radiation (W/m^2)")
        self.ax.axes.set_xlabel("Time (h)")
        self.ax.axes.set_ylabel("Radiation (W/m^2)")

        #Eneable de widgets necesarios
        self.btnDetener.hide()
        self.btnReinicio.hide()
        self.btnSeguimiento.hide()
        if(self.have_internet() == False):
            self.rbtnDireccion.setEnabled(0)
        
        #Variables de check
        self.rbtnsel = False
        self.direccion = None
        self.coordenad = None
        self.detener = False
        self.orientarZ = False
        self.setZero = False
        self.micro_board = None
        self.solarTracking = False
        
        #Variables inicisles
        self.port = None#Puerto seleccionado
        self.lat = None #latitud    
        self.lon = None #longitud
        
        #Variable texto
        self.text = False
        
        #variables inclinacion,azimuth
        self.psi = 0
        self.alpha = 0
        self.algo = 0
        
        #Variables serial arduino
        self.pulAz = 0
        self.mfAz = 1
        self.dirAz = 0
        self.enInclinacion = 0
        self.dirInclinacion = 0
        
        #Variables de sensores de entrada
        self.Mx = 0
        self.My = 0
        self.Mz = 0
        self.Pitch = 0
        self.Roll = 0
        self.radGlobal = 0
        self.radDirect = 0
        self.magnetometro = 0
        self.brujula = 0
        self.end = "N"
        self.end2 = "N"
        self.errorPitch = 0
        
        #Variable tipo de adquisicion
        self.modo = "o"
        
        #Variables estados anteriores
        self.azimuthAnterior = 180

        #LCD number activacion
        self.lcdHora.setDigitCount(5)
        self.lcdLatitud.setDigitCount(6)
        self.lcdLongitud.setDigitCount(6)
        self.lcdInclinacion.setDigitCount(5)
        self.lcdAzimuth.setDigitCount(6)
        
        self.comboBox.addItem("---")
        ports = self.SerialPorts()
        for port in ports:
            self.comboBox.addItem(str(port))
        # self.cmbStep.maximum(60)
        #Cosa de process
        self._process = QtCore.QProcess(self)
        
        #Combo de Step
        self.cmbStep.setMaximum(30)
        self.tabManual.setEnabled(0)
        self.spbAzimuth.setMaximum(359)
        
        #Acciones de los elementos
        self.comboBox.activated.connect(self.on_port_changed)
        self.rbtnDireccion.clicked.connect(self.direccion_is_checked)
        self.rbtnCoordenadas.clicked.connect(self.coordenadas_is_checked)
        self.btnIniciar.clicked.connect(self.on_communication)
        self.btnSeguimiento.clicked.connect(self.on_start)
        self.btnDetener.clicked.connect(self.on_stop)
        self.btnReinicio.clicked.connect(self.on_restart)
        self.btnAzimuthN.clicked.connect(self.move_azimuth_N)
        self.btnAzimuthP.clicked.connect(self.move_azimuth_P)
        self.btnInclinacionM.clicked.connect(self.move_inclinacion_N)
        self.btnInclinacionP.clicked.connect(self. move_inclinacion_P)
        self.btnSetZeroA.clicked.connect(self.set_new_zeroA)
        self.btnGuardar.clicked.connect(self.save_file)
        
        #Accion para solar tracking == True
        self.worker = WorkerThread()
        
        #Arrays para graficar
        self.y1 = np.asarray([])
        self.y2 = np.asarray([])
        self.x = np.asarray([])
        # Variable placa de Arduino
        self.micro_board = None

#Funciones que tienen que tienen que tratar con widgets directamente-----INICIO
    #Internet prueba--------------------------------------------------INICIO        
    def have_internet(self):
        conn = httplib.HTTPConnection("www.google.com", timeout=5)
        try:
            conn.request("HEAD", "/")
            conn.close()
            return True
        except:
            conn.close()
            return False
    #Internet prueba-----------------------------------------------------FIN
    #ComboBox codigo para COM-----------------------------------------INICIO
    #Obtener lista de puertos de entrada
    def SerialPorts(self) -> list:
        if (sys.platform.startswith('win')):
            ports = ['COM%s' % (i+1) for i in range(256)]
        elif (sys.platform.startswith('linux') 
              or sys.platform.startswith('cygwin')):       
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif (sys.platform.startswith('darwin')):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result
    #Seleccion de puerto
    def on_port_changed(self, combo):
        aviable_port = self.comboBox.itemText(combo)
        if (aviable_port is not None):
            self.port = aviable_port
            print("Selected port = %s" % self.port)
        else:
            self.port = None
            self.on_no_port_aviable(self)
    #Cuando el Step cambia
    def on_step_changed(self, step):
        self.paso = int(self.cmbStep.itemText(step))
        print(self.paso)
    #Cuando el puerto no esta disponible
    def on_no_port_aviable(self):
        dlg_board = QMessageBox()
        dlg_board.setWindowTitle("COM Port ERROR")
        str_dlg_board = "No serial port available"
        dlg_board.setText(str_dlg_board)
        dlg_board.setStandardButtons(QMessageBox.Ok)
        dlg_board.setIcon(QMessageBox.Warning)
        dlg_board.exec_()
    #ComboBox codigo para COM--------------------------------------------FIN
    #Conexión fallida con el arduino----------------------------------INICIO    
    def on_failed_connection(self):
        dlg_board = QMessageBox()
        dlg_board.setWindowTitle("COM Port ERROR")
        str_dlg_board = "Board communication can not be read"
        str_dlg_board += " Or it wasn't selected"
        dlg_board.setText(str_dlg_board)
        dlg_board.setStandardButtons(QMessageBox.Ok)
        dlg_board.setIcon(QMessageBox.Warning)
        dlg_board.exec_()
    #Conexion fallida con el arduino-------------------------------------FIN
    #Com serial vacia-------------------------------------------------INICIO    
    def on_failed_info(self):
        dlg_board = QMessageBox()
        dlg_board.setWindowTitle("No info ERROR")
        str_dlg_board = "No info has been read from arduino"
        dlg_board.setText(str_dlg_board)
        dlg_board.setStandardButtons(QMessageBox.Ok)
        dlg_board.setIcon(QMessageBox.Warning)
        dlg_board.exec_()
    #Com serial vacia----------------------------------------------------FIN
    #Campos no llenos-------------------------------------------------INICIO
    def on_no_data(self):
        dlg_board = QMessageBox()
        dlg_board.setWindowTitle("Data Empty")
        str_dlg_board = "Missing data or no such values"
        dlg_board.setText(str_dlg_board)
        dlg_board.setStandardButtons(QMessageBox.Ok)
        dlg_board.setIcon(QMessageBox.Warning)
        dlg_board.exec_()
    #Campos no llenos----------------------------------------------------FIN
    #Campos no llenos-------------------------------------------------INICIO
    def on_no_working_time(self):
        dlg_board = QMessageBox()
        dlg_board.setWindowTitle("Working time")
        str_dlg_board = "It´s not time to work"
        dlg_board.setText(str_dlg_board)
        dlg_board.setStandardButtons(QMessageBox.Ok)
        dlg_board.setIcon(QMessageBox.Warning)
        dlg_board.exec_()
    #Campos no llenos----------------------------------------------------FIN
    #Funcion para los displays----------------------------------------INICIO
    def set_display(self):
        if(self.minutos >= 10):
            self.lcdHora.display(str(self.hora)+":"+str(self.minutos))
        else:
            self.lcdHora.display(str(self.hora)+":0"+str(self.minutos))
        self.lcdAzimuth.display("{0:.2f}". format(self.azimuthAnterior))
        self.lcdInclinacion.display("{0:.2f}". format(self.algo))
    #Funcion para los displays-------------------------------------------FIN
#Funciones que tienen que tienen que tratar con widgets directamente--------FIN

#FUnciones para check----------------------------------------------------INICIO
    #rbtnDireccion rbtnCoordenadas InDireccion -----------------------INICIO
    def direccion_is_checked(self):
        self.direccion = True
        self.coordenad = False
        self.rbtnsel = True
    
    def coordenadas_is_checked(self):
        self.direccion = False
        self.coordenad = True
        self.rbtnsel = True
    
    def selection_coord(self):
        if (self.direccion == True):
            print("Coordenadas por direccion")
            self.direccionInt()
        elif (self.coordenad == True):
            print("Coordenadas entrada manual")
            self.ubicacion()
            
    def all_variables(self):
        if(self.rbtnsel == False or self.inDireccion.text() == "" or self.port == None):
            return False
        else:
            return True
            
    def set_zero_activated(self):
        if(self.cbxPuntoZ.isChecked()==True):
            print("Set zero")
            return True
        else:
            print("No set zero")
            return False
    #rbtnDireccion rbtnCoordenadas InDireccion --------------------------FIN
#Funciones para check-------------------------------------------------------FIN
#------------------------------------------------------------------------------
#Funciones de botnones principales---------------------------------------------
#------------------------------------------------------------------------------
#on_communication programa para cuando se inicie la comunicacion --------INICIO
    def on_communication(self):
        #Campos llenados?
        if(self.all_variables() == False):
            print("Data empty")
            if(self.rbtnsel == False or self.inDireccion.text() == ""):
                self.on_no_data()
            else:
                self.on_no_port_aviable()
        else:
            #Comunicacion con el arduino y mostrar datos--------------INICIO
            take_data = False
            if(self.micro_board != None):
                self.micro_board.close()
            if(self.port != None):
                try:
                    port = str(self.port)
                    baudrate = 115200
                    self.micro_board = serial.Serial(port,baudrate,timeout=2)
                    take_data = True                    
                except:
                    self.on_failed_connection()
                    take_data = False
            if(take_data == True):    
                self.detener = False
                self.tabManual.setEnabled(1)
                self.btnSeguimiento.show()
                self.btnReinicio.show()
                self.btnIniciar.setEnabled(0)
                self.rbtnCoordenadas.setEnabled(0)
                self.rbtnDireccion.setEnabled(0)
                self.inDireccion.setEnabled(0)
                self.comboBox.setEnabled(0)
                self.cbxPuntoZ.setEnabled(0)
                self.text = self.inDireccion.text()
                self.selection_coord()
                self.lcdLatitud.display("{0:.2f}". format(self.lat))
                self.lcdLongitud.display("{0:.2f}". format(self.lon))
                self.horaReal()
                self.algoritmo()
                self.set_display()
                self.sendInfo()
                self.azimuthAnterior = 0
            #Comunicacion con el arduino y mostrar datos----------------FIN
            #Que hacer si Orientar Zero activado---------------------INICIO
            if (self.set_zero_activated() == True):
                #Establecemos inclinacion a 90°
                self.modo = "I"
                self.algo = 90
                self.sendInfo()
                self.readInfo()
                #Esperar a que termine de inclinarse
                while(self.end != "T"):
                    self.readInfo()
                #Lee la informacion y promedia para obtener la posición
                self.modo = "o"
                self.sendInfo()
                self.readInfo()
                self.set_display()
            else:
                self.azimuthAnterior = 180
                self.set_display()
            #Que hacer si Orientar Zero activado-------------------------FIN
#on_communication programa para cuando se inicie la comunicacion -----------FIN
#on_start programa para cuando se active inicio -------------------------INICIO
    def on_start(self):
        self.btnSeguimiento.hide()
        self.btnDetener.show()
        self.tabManual.setEnabled(0)
        #Para que el mecanismo no trabaje en una inclinacion menor
        if(self.alpha < 25):
            print("No working time")
            self.on_no_working_time()
            self.btnDetener.hide()
            self.btnSeguimiento.show()
            return 0
        while(self.orientarZ == True):
            print("setting Zero")
            #Mover a la posicion del sol
            self.orientarZ = False
        print("Starting solar tracking")
        # self.timer = QTimer()
        # self.timer.setInterval(10000)
        # self.timer.timeout.connect(self.prueba)
        # self.timer.start()
        self.solarTracking = True
        self.worker.start()
        self.worker.update.connect(self.rutina)
#on_Start programa para cuando se active inicio ----------------------------FIN

    def rutina(self,val):
        print(val)
        if(val == True):
            print("Prueba")
            #Hora actual
            self.horaReal()
            #Llamar al algoritmo
            self.algoritmo()
            #Iniciar control de inclinacion
            self.modo = "I"
            self.algo = self.algo + self.errorPitch
            self.sendInfo()
            self.readInfo()
            while(self.end != "T"):
                self.readInfo()
            #Segun azimuth calcular pasos y sentido
            self.micro_board.flushInput()
            self.modo = "M"
            #Moverse
            self.movimientoAzimuth(self.psi, self.azimuthAnterior)
            self.sendInfo()
            print("Azimuth")
            self.azimuthAnterior = self.psi
            while(self.end2 != "T"):
                self.readInfo()
            self.readInfo()
            self.readInfo()
            sleep(0.2)
            self.micro_board.flushInput()
            self.modo = "R"
            self.sendInfo()
            self.readInfo()
            self.readInfo()
            print("Radiacion")
            time.sleep(5)
            self.modo = "o"
            self.Graficar()
            #Actualizar display
            self.set_display()
            #graficar sensores
        else:
            print("adeus")
            #No hacer nancy

#on_stopt programa para cuando se active detener ------------------------INICIO
    def on_stop(self):
        self.detener = True
        self.btnSeguimiento.show()
        self.btnDetener.hide()
        self.tabManual.setEnabled(1)
        self.solarTracking = False
        self.worker.terminate()
        print("se detuvo el seguimiento")
#on_stopt programa para cuando se active detener ---------------------------FIN

#on_restart programa para cuando se reinicie ----------------------------INICIO
    def on_restart(self):
        self.detener = True
        self.btnDetener.hide()
        self.btnReinicio.hide()
        self.btnSeguimiento.hide()
        self.btnIniciar.setEnabled(1)
        self.btnSeguimiento.setEnabled(1)
        self.rbtnCoordenadas.setEnabled(1)
        self.rbtnDireccion.setEnabled(1)
        self.inDireccion.setEnabled(1)
        self.comboBox.setEnabled(1)
        self.cbxPuntoZ.setEnabled(1)
        self.tabManual.setEnabled(1)
        self.tabManual.setEnabled(0)
        self.solarTracking = False
        self.dirAz = 0
        self.modo = "o"
        self.mfAz = 0
        self.pulAz  = 0
        #self.lcdLatitud.display()
        #self.lcdLongitud.display()
        self.worker.terminate()
        print("se detuvo el seguimiento")
        time.sleep(1)
        self.micro_board.close()
#on_restart programa para cuando se reinicie -------------------------------FIN
#on_set_new_zero---------------------------------------------------------INICIO
    def set_new_zeroA(self):
        self.azimuthAnterior = self.spbAzimuth.value()
        self.set_display()
    
    def set_new_zeroI(self):
        self.errorPitch = 0
        self.set_display()
#on_set_new_zero------------------------------------------------------------FIN
#------------------------------------------------------------------------------
#Funciones de programa---------------------------------------------------------
#------------------------------------------------------------------------------
#Funcion para mover azimuth manual---------------------------------------INICIO
    #Funcion para azimuth negativo------------------------------------INICIO
    def move_azimuth_N(self):
        self.paso = self.cmbStep.value()
        self.azimuthAnterior = self.azimuthAnterior - self.paso
        self.pulAz = self.calculoPasos(self.paso, 0)
        self.dirAz = 1
        self.modo = "M"
        self.sendInfo()
        self.set_display()
        print(self.azimuthAnterior)
    #Funcion para azimuth negativo---------------------------------------FIN
    #Funcion para azimuth positivo------------------------------------INICIO
    def move_azimuth_P(self):
        self.paso = self.cmbStep.value()
        self.azimuthAnterior = self.azimuthAnterior + self.paso
        self.pulAz = self.calculoPasos(self.paso, 0)
        self.dirAz = 0
        self.modo = "M"
        self.sendInfo()
        self.set_display()
        print(self.azimuthAnterior)
    #Funcion para azimuth positivo---------------------------------------FIN
#Funcion para mover azimuth manual---------------------------------------INICIO
    #Funcion para inclinacion negativo--------------------------------INICIO
    def move_inclinacion_N(self):
        self.paso = self.cmbStep.value()
        self.modo = "I"
        self.sendInfo()
        self.readInfo()
        self.algo = self.Pitch - self.paso
        self.sendInfo()
        self.set_display()
    #Funcion para azimuth negativo--------------------------------------FIN
    #Funcion para azimuth positivo------------------------------------INICIO
    def move_inclinacion_P(self):
        self.paso = self.cmbStep.value()
        self.modo = "I"
        self.sendInfo()
        self.readInfo()
        self.algo = self.Pitch + self.paso
        self.sendInfo()
        self.set_display()
    #Funcion para azimuth positivo---------------------------------------FIN
#Funciones con procesamiento de lectura de datos-------------------------INICIO
    #Lectura de datos-------------------------------------------------INICIO
    def readInfo(self):
        print("Reading info...")
        temp = str(self.micro_board.readline().decode('cp437'))
        sensores = temp.replace("\r\n","")
        print("Info read")
        time.sleep(0.1)
        if(sensores == ""):
            self.on_failed_info()
            sensores = "0,0,0,0,0"
        self.micro_board.flushInput()
        if(self.modo == "R"):
            self.radDirect = float(sensores.split(",")[3])
            self.radGlobal = float(sensores.split(",")[4])
        elif(self.modo == "I"):
            self.Pitch = int(sensores.split(",")[0])
            self.end = sensores.split(",")[1]
        elif(self.modo == "M"):
            self.end2 = sensores.split(",")[2]
        self.lblRead.setText(sensores)
        print(sensores)
        time.sleep(0.4)
    #Lectura de datos----------------------------------------------------FIN
    
    #Envío de datos---------------------------------------------------INICIO
    def sendInfo(self):
        stringSerial = ""
        stringSerial = self.modo + ","
        stringSerial += '{:05d}'.format(self.pulAz) + ","
        stringSerial += '{:01d}'.format(self.mfAz) + ","
        stringSerial += '{:01d}'.format(self.dirAz) + ","
        stringSerial += '{:02d}'.format(self.algo)
        #stringSerial += str(self.pulAz)+","+str(self.mfAz)+","+str(self.dirAz)+","
        #stringSerial += str(int(self.alpha))
        self.micro_board.write(stringSerial.encode()) #'utf-8'
        self.lblSerial.setText(stringSerial)
        print(stringSerial)
        time.sleep(2)
    #Envío de datos------------------------------------------------------FIN
    #Datos de magnetometro procesados---------------------------------INICIO
    def compass(self):
        MxH = self.Mx
        MyH = self.My
        if(MxH > 0):
            alfa = 90 - rd(atan(MyH/MxH))
        elif(MxH < 0):
            alfa = 270 - rd(atan(MyH/MxH))
        elif(MxH == 0 and MyH < 0):
            alfa = 0
        elif(MxH == 0 and MyH > 0):
            alfa = 180
        self.magnetometro = int(alfa)
        print(self.magnetometro)
    #Datos de magnetometro procesados------------------------------------FIN
#Funciones con procesamiento de lectura de datos----------------------------FIN

    def direccionInt(self):
        loc = Nominatim(user_agent="GetLoc")
        getLoc = loc.geocode(self.text)
        print("Dirección: ",getLoc.address)
        self.lat = getLoc.latitude
        self.lon = getLoc.longitude
    
    def ubicacion(self):
        temporal = self.text.split(",")
        self.lat = float(temporal[0])
        self.lon = float(temporal[1])

    def algoritmo(self):
        if (self.mes == 1):
            dn = self.dia
        elif(self.mes == 2):
            dn = 31+self.dia
        elif(self.mes == 3):
            dn = 31+28+self.dia
        elif(self.mes == 4):
            dn = 31+28+31+self.dia
        elif(self.mes == 5):
            dn = 31+28+31+30+self.dia
        elif(self.mes == 6):
            dn = 31+28+31+30+31+self.dia
        elif(self.mes == 7):
            dn = 31+28+31+30+31+30+self.dia
        elif(self.mes == 8):
            dn = 31+28+31+30+31+30+31+self.dia
        elif(self.mes == 9):
            dn = 31+28+31+30+31+30+31+31+self.dia
        elif(self.mes == 10):
            dn = 31+28+31+30+31+30+31+31+30+self.dia
        elif(self.mes == 11):
            dn = 31+28+31+30+31+30+31+31+30+31+self.dia
        elif(self.mes ==12):
            dn = 31+28+31+30+31+30+31+31+30+31+30+self.dia
        
        ggamma = 2*pi*(dn-1)/365
        delta = (0.006918-0.399912*cos(ggamma)+0.070257*sin(ggamma)-0.006758*cos(2*ggamma)
                  +0.000907*sin(2*ggamma)-0.002697*cos(3*ggamma)+0.00148*sin(3*ggamma))
        
        Et = (((0.000075 + 0.001868*cos(ggamma))-(0.032077*sin(ggamma))
               -(0.014615*cos(2*ggamma))-(0.04089*sin(2*ggamma)))*(229.18))
        Et = Et/60
        
        hora_aparente = self.hrmin + (((self.lon-self.UTC*15)/15)) + Et
        omega = (12-hora_aparente)*15
        omega = dr(omega)
        phi = dr(self.lat)
        
        incli = np.arccos((sin(delta)*sin(phi))+(cos(delta)*cos(phi)*cos(omega)))
        incli = rd(incli)
        self.alpha = 90-incli
        self.alpha = dr(self.alpha)
        
        self.psi = np.arccos(((sin(self.alpha)*sin(phi))-sin(delta))/(cos(self.alpha)*cos(phi)))
        
        if (hora_aparente > 12):
            self.psi = - self.psi
        else:
            self.psi = self.psi
        
        self.alpha = rd(self.alpha)
        self.psi = rd(self.psi)
        self.psi = 180-self.psi
        print(self.psi)
        print(self.alpha)
        self.algo = int(self.alpha)
    
    def horaReal(self):
        self.start = datetime.now()
        self.hora = self.start.hour
        self.minutos = self.start.minute
        self.hrmin = self.hora + self.minutos/60
        self.dia = self.start.day
        self.mes = self.start.month
        self.UTC = -datetime.now(pytz.utc).hour+datetime.now().hour
        #return(hrmin,UTC,dia,mes,hora,minutos)
    
    # def calculoPosicion(self):
    #     fecha = self.horaReal()
    #     print("Fecha: ",fecha)
    #     posicion = algoritmo(coord[0],coord[1],fecha[0],fecha[1],fecha[2],fecha[3])
    #     print("Azimuth: ",posicion[0]," Inclinación: ",posicion[1])
    #     return posicion
    
    # #Esta funcion es para setear zero azimuth
    # def setZeroAzimuth(self,mgntmtr,angDeseado):
    #     #Aqui hacemos lazo cerrado con magnetometro
    #     if(mgntmtr < angDeseado): #Si es menor se supone que debe avanzar mas
    #         self.pulAz = 1
    #         self.mfAz =  0
    #         self.dirAz = 1
    #         return False
    #     elif(mgntmtr > angDeseado):
    #         self.pulAz = 1
    #         self.mfAz =  0
    #         self.dirAz = 0
    #         return False
    #     else:
    #         self.pulAz = 0
    #         self.mfAz =  1
    #         self.dirAz = 0
    #         return True
    
    # def temporizadorAngulos(self):
    #     azimuth=0
    #     self.horaReal()
    #     minReal = self.minutos
    #     self.algoritmo()
    #     if(self.alpha >= 25):
    #         if(minReal%6 == 3):
    #             print("estoy mandando datos")
    #             azimuth = self.psi
    #             inclinacio = self.alpha
    #             self.readInfo()
    #             self.movimientoAzimuth(azimuth, self.azimuthAnterior)
    #             self.mfAz =  0
    #             avFiltro = self.avSensor
    #             self.controlInclinacion(avFiltro, inclinacio)
    #             self.sendInfo()
    #         else:
    #             self.azimuthAnterior = azimuth
    #             print("No hago nada")
    #     else: print("No hago nada X2")
#Funciones para controlar azimuth ---------------------------------------INICIO
    #Esta funcion será para controlar el movimiento de azimut
    def movimientoAzimuth(self,azimuth,azimuhtAnterior):
        pulsos = self.calculoPasos(azimuth,azimuhtAnterior)
        self.pulAz = abs(pulsos)
        self.dirAz = self.sentidoAzimut(pulsos)
    
    def calculoPasos(self,azimut,azimutAnterior):
        N = 30
        P = 400
        dAzimut = azimut - azimutAnterior
        pasos = int(N*dAzimut*P/360)
        return pasos
    
    def sentidoAzimut(self,pasos):
        if(pasos < 0): dirAzimut = 1
        else: dirAzimut = 0
        return dirAzimut
    
    def Graficar(self):
        self.y2 = np.append(self.y2,self.radDirect)
        self.y1 = np.append(self.y1,self.radGlobal)
        self.x = np.append(self.x,self.hrmin)
        self.ax.clear()
        self.ax2.clear()
        self.ax2.axes.set_xlabel("Time (h)")
        self.ax2.axes.set_ylabel("Radiation (W/m^2)")
        self.ax.axes.set_xlabel("Time (h)")
        self.ax.axes.set_ylabel("Radiation (W/m^2)")
        self.ax.axes.plot(self.x,self.y1)
        self.ax2.axes.plot(self.x,self.y2)
        self.canvas.draw()
        self.canvas2.draw()
        
#Funciones para controlar azimuth ------------------------------------------FIN

    def save_file(self):
        print("Save data")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self,
                                                  "QFileDialog.getSaveFileName()", ""
                                                  , "csv Files(*.csv);;All Files (*)",
                                                  options=options)
        filename = filename + ".csv"
        if (filename):
            file = open(filename, 'w')
            file.write("Time_(h), Global-Radiation_(W/m^2), Direct-Radiation_(W/m^2)" + "\n")
            for i in range(len(self.x)):
                file.write(self.x[i] + self.y1[i] + self.y2[i] + "\n")
            file.close()

    #Esta funcion es para controlar la inclinacion
    # def controlInclinacion(self,avFiltro,inclinacio):
    #     if(inclinacio > avFiltro):
    #         self.dirInclinacion = 1
    #         self.enInclinacion = 1
    #     elif(inclinacio < avFiltro):
    #         self.dirInclinacion = 0
    #         self.enInclinacion = 1
    #     else: self.enInclinacion = 0
#En este solo vamos a hacer la cuenta de cada seis minutos,
#para que mande una señal que active el proceso de azimuth e inclinacion
#Cada que emite se ejecuta el codigo por lo cual nos sirve para que sea una especie de reloj
class WorkerThread(QThread):
    update = pyqtSignal(bool)
    def run(self):
        while(True):
            start = datetime.now()
            minutos = start.minute
            if(minutos%3 == 0):
                print("Iniciando movimiento")
                activa = True
                self.update.emit(activa)
            else:
                print("Sleep")
                activa = False
                self.update.emit(activa)
            sleep(60)
     
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mi_app = VentanaPrincipal()
    mi_app.show()
    sys.exit(app.exec())