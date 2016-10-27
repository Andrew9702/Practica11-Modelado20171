import sys
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from xmlrpc.client import ServerProxy
 
clienteGui = uic.loadUiType("cliente2.ui")[0] #Se carga la interfaz de tipo ui, esta vez del cliente.


class Cliente(QtGui.QMainWindow, clienteGui):

	#Inicia la ventana para el cliente
 	def __init__(self, parent=None):
 		QtGui.QMainWindow.__init__(self, parent)
 		self.setupUi(self) 

 		#Expande las celdas al tamaño de la widget
 		self.tableWidget.horizontalHeader().setResizeMode(QHeaderView.Stretch) 
 		self.tableWidget.verticalHeader().setResizeMode(QHeaderView.Stretch) 
 		self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
 		self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 

 		#Botones funcionales
 		self.ping.clicked.connect(self.lanzarPing)
 		self.participar.clicked.connect(self.partyHard)
 		self.tableWidget.keyPressEvent = self.keyPressEvent

 		self.guardaCoords=None
 		self.timer = QTimer()
 		self.timer.timeout.connect(self.comoEsta)
 		self.dire=0

 	#Lanza un ping para comprobar que la conexion es exitosa
 	def lanzarPing(self):
 		self.ping.setText("Piging...")
 		try:
 			self.direccion = "http://" + self.url.text() + ":" + str(self.finder())
 			self.cliente = ServerProxy(self.direccion) 
 			pong = self.cliente.ping()
 			self.primeraves= True
 			self.ping.setText("¡Pong!")
 			self.timer.start(self.cliente.estado_del_juego()["espera"])
 		except:
 			self.ping.setText("No pong :(\nInténtalo de nuevo")

 	#Actualiza la widget a como esta la del juego
 	def comoEsta(self):
 		estado = self.cliente.estado_del_juego()
 		self.timer.setInterval(estado["espera"])
 		self.tableWidget.setColumnCount(estado['tamY']) #Inicia las columnas con el tamaño de las que tiene el server
 		self.tableWidget.setRowCount(estado['tamX']) #Inicia las filas con el tamaño de las que tiene el server
 		listaVibs = estado['vivoras']
 		self.borraTodo(self.guardaCoords)
 		for vibora in listaVibs:
 			self.spawnSnake(vibora['camino'],vibora['color'])
 		self.guardaCoords = estado['vivoras']
 			
 	#Borra todas las serpiente del tableWidget
 	def borraTodo(self,viboras):
 		if viboras == None:
 			return
 		else:
 			for vibora in viboras:
 				self.erase(vibora['camino'])

    #Crea y aparece a la serpiente que hace spawn en servidor
 	def spawnSnake(self, coordenadas, color):
 		cabezaSnake = QTableWidgetItem()
 		cuerpoSnake1 = QTableWidgetItem()
 		cuerpoSnake2 = QTableWidgetItem()
 		cuerpoSnake3 = QTableWidgetItem()
 		colaSnake = QTableWidgetItem()
 		cabezaSnake.setBackgroundColor(QtGui.QColor(color[0],color[1],color[2]))
 		cuerpoSnake1.setBackgroundColor(QtGui.QColor(color[0],color[1],color[2]))
 		cuerpoSnake2.setBackgroundColor(QtGui.QColor(color[0],color[1],color[2]))
 		cuerpoSnake3.setBackgroundColor(QtGui.QColor(color[0],color[1],color[2]))
 		colaSnake.setBackgroundColor(QtGui.QColor(color[0],color[1],color[2]))
 		self.tableWidget.setItem(coordenadas[0], coordenadas[1], cabezaSnake)
 		self.tableWidget.setItem(coordenadas[2], coordenadas[3], cuerpoSnake1)
 		self.tableWidget.setItem(coordenadas[4], coordenadas[5], cuerpoSnake2)
 		self.tableWidget.setItem(coordenadas[6], coordenadas[7], cuerpoSnake3)
 		self.tableWidget.setItem(coordenadas[8], coordenadas[9], colaSnake)

 	#Borra a la serpiente, esto para el algoritmo de moverse
 	def erase(self,coordenadas):
 		self.tableWidget.takeItem(coordenadas[0], coordenadas[1])
 		self.tableWidget.takeItem(coordenadas[2], coordenadas[3])
 		self.tableWidget.takeItem(coordenadas[4], coordenadas[5])
 		self.tableWidget.takeItem(coordenadas[6], coordenadas[7])
 		self.tableWidget.takeItem(coordenadas[8], coordenadas[9])

 	#Te informa acerca del puerto que se usa en la interfaz
 	def finder(self):
 		puerto = 0
 		if self.puerto.value() == 0:
 			puerto = 8000
 			self.puerto.setValue(puerto)
 		else:
 			puerto = self.puerto.value()
 			self.puerto.setValue(puerto)
 		return puerto


 	#Crea una nueva serpiente y la pinta en el servidor y en el cliente
 	def partyHard(self):
 		snaker = self.cliente.yo_juego()
 		self.id.setText(str(snaker['id']))
 		self.color.setText(str(snaker['color']))
 		self.participar.hide()

 	#Controles para la serpiente del servidor
 	def keyPressEvent(self,event):
 		if event.key() == QtCore.Qt.Key_Left and self.dire != 1:
 			self.cliente.camba_direccion(self.id.text(), 3)
 			self.dire = 3
 		elif event.key() == QtCore.Qt.Key_Right and self.dire != 3:
 			self.cliente.camba_direccion(self.id.text(), 1)
 			self.dire = 1
 		elif event.key() == QtCore.Qt.Key_Up and self.dire != 2:
 			self.cliente.camba_direccion(self.id.text(), 0)
 			self.dire = 0
 		elif event.key() == QtCore.Qt.Key_Down and self.dire != 0:
 			self.cliente.camba_direccion(self.id.text(), 2)
 			self.dire= 2

#Inicia la aplicacion.
def main():
    app = QtGui.QApplication(sys.argv)
    win = Cliente()
    win.show()
    app.exec_()
    
main()
