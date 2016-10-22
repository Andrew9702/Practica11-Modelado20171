import sys
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from xmlrpc.client import ServerProxy
 
clienteGui = uic.loadUiType("cliente2.ui")[0] #Se carga la interfaz de tipo ui, esta vez del cliente.


class Cliente(QtGui.QMainWindow, clienteGui):

 	def __init__(self, parent=None):
 		QtGui.QMainWindow.__init__(self, parent)
 		self.setupUi(self) #Se inicializa la interfaz de ui
 		self.tableWidget.horizontalHeader().setResizeMode(QHeaderView.Stretch) #Como su nombre lo dice estira a las columnas horizontales para adaptarse a la widget
 		self.tableWidget.verticalHeader().setResizeMode(QHeaderView.Stretch) #Lo mismo para las verticales (En esencia lo mismo que el servidor)
 		self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) #Cuando las celdas son bastantes, la scrollbar aparece, este basicamente las hace desaparecer
 		self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) #Tambien las verticales
 		self.ping.clicked.connect(self.lanzarPing)
 		self.participar.clicked.connect(self.partyHard)
 		self.direccion = "http://" + self.url.text() + ":" + str(self.finder())
 		self.cliente = ServerProxy(self.direccion) 
 		self.tableWidget.keyPressEvent = self.keyPressEvent

 	def finder(self):
 		puerto = 0
 		if self.puerto.value() == 0:
 			puerto = 8000
 		else:
 			puerto = self.puerto.value()
 		return puerto

 	def lanzarPing(self):
 		self.ping.setText("Piging...")
 		if self.cliente.ping() == "¡Pong!":
 			self.ping.setText("¡Pong!")
 		else:
 			self.ping.setText("No pong :(")

 	def partyHard(self):
 		snaker = self.cliente.yo_juego()
 		self.id.setText(str(snaker['id']))
 		self.color.setText(str(snaker['color']))
 		#self.participar.hide()

 	def keyPressEvent(self,event):
 		if event.key() == QtCore.Qt.Key_Left and self.dire != 1:
 			self.dire= 3
 		elif event.key() == QtCore.Qt.Key_Right and self.dire != 3:
 			self.dire= 1
 		elif event.key() == QtCore.Qt.Key_Up and self.dire != 2:
 			self.dire= 0
 		elif event.key() == QtCore.Qt.Key_Down and self.dire != 0:
 			self.dire= 2

 	def mueveDesdeCliente(self):
 		self.cliente.camba_direccion(self.id.text(), 2)



#Inicia la aplicacion.
def main():
    app = QtGui.QApplication(sys.argv)
    win = Cliente()
    win.show()
    app.exec_()
    
main()
