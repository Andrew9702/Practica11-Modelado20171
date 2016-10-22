import sys
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import random
import uuid

servidorUi = uic.loadUiType("servidor2.ui")[0] #Se carga la interfaz de tipo ui del servidor
 
class Servidor(QtGui.QMainWindow, servidorUi):

	def __init__(self, parent=None):#Constructor de la ventana
		QtGui.QMainWindow.__init__(self, parent)
		self.setupUi(self)#Inicializa la interfaz del tipo ui

		self.tableWidget.horizontalHeader().setResizeMode(QHeaderView.Stretch) #Como su nombre lo dice estira a las columnas horizontales para adaptarse a la widget
		self.tableWidget.verticalHeader().setResizeMode(QHeaderView.Stretch) #Lo mismo para las verticales
		self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) #Cuando las celdas son bastantes, la scrollbar aparece, este basicamente las hace desaparecer
		self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) #Tambien las verticales (Con las de 20 columnas, 20 filas, aparecía)

		self.columnas.setMaximum(99) #Ajusta cuantos se puede recibir como maximo en la spinbox para las columnas
		self.columnas.setMinimum(10) #Ajusta cuantos se puede recibir como minimo en la spinbox para las columnas
		self.columnas.valueChanged.connect(self.ajustaColumnas) #Conecta los valores de la spinbox al metodo

		self.filas.setMaximum(99) #Ajusta cuantos se puede recibir como maximo en la spinbox para las filas
		self.filas.setMinimum(10) #Ajusta cuantos se puede recibir como minimo en la spinbox para las filas

		self.espera.setMaximum(999)
		self.espera.setMinimum(10)
		self.espera.setValue(150)

		self.timeout.valueChanged.connect(self.esperame)

		self.filas.valueChanged.connect(self.ajustaRenglones)
		self.espera.valueChanged.connect(self.speed) #Conecta los valores de la spinbox con el metodo

		self.tableWidget.setColumnCount(self.columnas.value()) #Inicia las columnas en el minimo de la spinbox
		self.tableWidget.setRowCount(self.filas.value()) #Inicia las filas en el minimo de la spinbox
		
		self.tableWidget.keyPressEvent = self.keyPressEvent
		self.iniciajuego.clicked.connect(self.playGameButton)
		self.pushButton_2.clicked.connect(self.termina)
		self.pushButton_2.hide()
		self.serverstart.clicked.connect(self.sirve)
		self.misViboras=[]
		self.misViborasInfo= []
		
	def ajustaColumnas(self, columnas): #Cambia las columnas cuando se cambia el valor de la spinbox
		self.tableWidget.setColumnCount(columnas)

	def ajustaRenglones(self, renglones): #Cambia las filas cuando se cambia el valor de la spinbox
		self.tableWidget.setRowCount(renglones)

	def speed(self, velocidad):
		self.timer.setInterval(velocidad)

	def esperame(self,cuanto):
		self.timeout.setValue(cuanto)

	def matame(self, bibora):
		if bibora.coordenadas[1] == bibora.coordenadas[9] and bibora.coordenadas[0] == bibora.coordenadas[8]:
			return True

		#Inicia el juego
	def playGameButton(self):
		if self.iniciajuego.text() == "Inicia Juego":
			self.snake = self.snakeMaker()
			self.dire = self.snake.direccion
			self.aparece(self.snake)
			self.misViboras.append(self.snake.id)
			self.iniciajuego.setText("Pausar el juego")#Cambia el texto del boton

			self.pushButton_2.show()

			self.timer = QTimer()
			self.timer.timeout.connect(self.mueve)
			self.timer.start(150)

			self.espera.setValue(150)

		elif self.iniciajuego.text() == "Pausar el juego":
			self.timer.stop()
			self.iniciajuego.setText("Reanudar juego")
		else: 
			self.timer.start(self.espera.value())
			self.iniciajuego.setText("Pausar el juego")
 

	def caminaDerecha(self,bibora):

		self.desaparece(bibora)
		bibora.todenuevo()
		bibora.coordenadas[8], bibora.coordenadas[9] = bibora.coordenadas[6], bibora.coordenadas[7]
		bibora.coordenadas[6], bibora.coordenadas[7] = bibora.coordenadas[4], bibora.coordenadas[5]
		bibora.coordenadas[4], bibora.coordenadas[5] = bibora.coordenadas[2], bibora.coordenadas[3]
		bibora.coordenadas[2], bibora.coordenadas[3] = bibora.coordenadas[0], bibora.coordenadas[1]
		bibora.coordenadas[0], bibora.coordenadas[1] = bibora.coordenadas[0], (bibora.coordenadas[1] + 1)% self.tableWidget.columnCount()
		self.aparece(bibora)

	def caminaIzquierda(self,bibora):

		self.desaparece(bibora)
		bibora.todenuevo()
		bibora.coordenadas[8], bibora.coordenadas[9] = bibora.coordenadas[6], bibora.coordenadas[7]
		bibora.coordenadas[6], bibora.coordenadas[7] = bibora.coordenadas[4], bibora.coordenadas[5]
		bibora.coordenadas[4], bibora.coordenadas[5] = bibora.coordenadas[2], bibora.coordenadas[3]
		bibora.coordenadas[2], bibora.coordenadas[3] = bibora.coordenadas[0], bibora.coordenadas[1]
		bibora.coordenadas[0], bibora.coordenadas[1] = bibora.coordenadas[0], (bibora.coordenadas[1] - 1)% self.tableWidget.columnCount()
		self.aparece(bibora)

	def caminaArriba(self,bibora):

		self.desaparece(bibora)
		bibora.todenuevo()
		bibora.coordenadas[8], bibora.coordenadas[9] = bibora.coordenadas[6], bibora.coordenadas[7]
		bibora.coordenadas[6], bibora.coordenadas[7] = bibora.coordenadas[4], bibora.coordenadas[5]
		bibora.coordenadas[4], bibora.coordenadas[5] = bibora.coordenadas[2], bibora.coordenadas[3]
		bibora.coordenadas[2], bibora.coordenadas[3] = bibora.coordenadas[0], bibora.coordenadas[1]
		bibora.coordenadas[0], bibora.coordenadas[1] = (bibora.coordenadas[0]-1)%self.tableWidget.rowCount(), bibora.coordenadas[1] 
		self.aparece(bibora)

	def caminaAbajo(self,bibora):

		self.desaparece(bibora)
		bibora.todenuevo()
		bibora.coordenadas[8], bibora.coordenadas[9] = bibora.coordenadas[6], bibora.coordenadas[7]
		bibora.coordenadas[6], bibora.coordenadas[7] = bibora.coordenadas[4], bibora.coordenadas[5]
		bibora.coordenadas[4], bibora.coordenadas[5] = bibora.coordenadas[2], bibora.coordenadas[3]
		bibora.coordenadas[2], bibora.coordenadas[3] = bibora.coordenadas[0], bibora.coordenadas[1]
		bibora.coordenadas[0], bibora.coordenadas[1] = (bibora.coordenadas[0]+1)%self.tableWidget.rowCount(), bibora.coordenadas[1] 
		self.aparece(bibora)

	def condicional(self, bibora):
		if self.dire == 0:
			self.mueveVib(0, bibora)
		elif self.dire == 1:
			self.mueveVib(1, bibora)
		elif self.dire == 2:
			self.mueveVib(2, bibora)
		elif self.dire == 3:  
			self.mueveVib(3, bibora)
		if self.matame(bibora):
			self.termina(bibora)

	def mueve(self):
		self.condicional(self.snake)

	def mueveVib(self, dir, bibora):
		if dir == 0:
			self.caminaArriba(bibora)
		elif dir == 1:
			self.caminaDerecha(bibora)
		elif dir == 2:
			self.caminaAbajo(bibora)
		elif self.dire == 3:
			self.caminaIzquierda(bibora)

	def keyPressEvent(self,event):
		if event.key() == QtCore.Qt.Key_Left and self.dire != 1:
			self.dire= 3
		elif event.key() == QtCore.Qt.Key_Right and self.dire != 3:
			self.dire= 1
		elif event.key() == QtCore.Qt.Key_Up and self.dire != 2:
			self.dire= 0
		elif event.key() == QtCore.Qt.Key_Down and self.dire != 0:
			self.dire= 2
	
	def termina(self, bibora):
		self.timer.stop()
		self.tableWidget.clear()
		self.iniciajuego.setText("Inicia Juego")#Cambia el texto del boton
		self.pushButton_2.hide()

	def sirve(self):
		if self.puerto.value()==0:
			self.servidor = SimpleXMLRPCServer((self.url.text(), 8000), allow_none= True) #Creamos nuestro objeto servidor en la clase
		else:
			self.servidor = SimpleXMLRPCServer((self.url.text(), self.puerto.value()), allow_none= True)

		self.servidor.timeout = self.timeout.value()
		self.servidor.register_function(self.ping)
		self.servidor.register_function(self.yo_juego)
		self.servidor.register_function(self.estado_del_juego)
		self.servidor.register_function(self.camba_direccion)
		self.krusty= QTimer(self)
		self.krusty.timeout.connect(self.cliente)
		self.krusty.start(100)

	#Así como en el ejemplo esta funcion va a escuchar por una llamada del cliente, si la escucha regresara una funcion
	def cliente(self):
		self.servidor.handle_request()

	#Metodo que regresa un pong por cada ping
	def ping(self):
		return "¡Pong!"

	#metodo que devuelve las propiedades de la vibora
	def yo_juego(self):
		self.snake = self.snakeMaker()
		self.snake.dir = self.snake.direccion
		self.aparece(self.snake)
		self.misViboras.append(self.snake)
		self.timer = QTimer()
		self.timer.timeout.connect(self.mueve)
		self.timer.start(150)
		return {"id": vivora.id, "color": {"r": vivora.color[0], "g": vivora.color[1], "b": vivora.color[2]}}

	def camba_direccion(self,identificador,direccioname):
		ladvd = None
		for i in range(len(self.misViboras)):
			if self.misViboras[i].id == identificador:
				ladvd = self.misViboras[i]
				ladvd.direccion = direccioname

	def estado_del_juego(self):
		return {"espera": self.espera.value(), "tamX": self.tableWidget.columnCount(), "tamY": self.tableWidget.rowCount(), "vivoras":self.misViborasInfo}


	#Creamos el objeto vivora
	def snakeMaker(self):
		id = self.identificadores() #Le damos en forma de string un identificador a la vivora
		color = self.colores()
		coordenadas = self.coordenates()
		vivora = Vivora(id,color,coordenadas,1)
		self.misViboras.append(vivora)
		self.misViborasInfo.append({"id": id, "camino": coordenadas, "color": color})
		return vivora

	def aparece(self,bibora):
		self.tableWidget.setItem(bibora.coordenadas[0], bibora.coordenadas[1], bibora.cabezaSnake)
		self.tableWidget.setItem(bibora.coordenadas[2], bibora.coordenadas[3], bibora.cuerpoSnake1)
		self.tableWidget.setItem(bibora.coordenadas[4], bibora.coordenadas[5], bibora.cuerpoSnake2)
		self.tableWidget.setItem(bibora.coordenadas[6], bibora.coordenadas[7], bibora.cuerpoSnake3)
		self.tableWidget.setItem(bibora.coordenadas[8], bibora.coordenadas[9], bibora.colaSnake)

	def desaparece(self,bibora):
		self.tableWidget.takeItem(bibora.coordenadas[0], bibora.coordenadas[1])
		self.tableWidget.takeItem(bibora.coordenadas[2], bibora.coordenadas[3])
		self.tableWidget.takeItem(bibora.coordenadas[4], bibora.coordenadas[5])
		self.tableWidget.takeItem(bibora.coordenadas[6], bibora.coordenadas[7])
		self.tableWidget.takeItem(bibora.coordenadas[8], bibora.coordenadas[9]) 

	#Dada la exigencia, crea una lista de colores que va de r,g,b y oscila entre 0 y 255, rango de colores de python
	def colores(self):
		r = random.randint(0,255)
		g = random.randint(0,255)
		b = random.randint(0,255)

		return [r,g,b]

	#Le asigna in id unico a la vivora
	def identificadores(self):
		return str(uuid.uuid4())

	#Tenemos una lista con las coordenadas de la vivora
	def coordenates(self):
		laX=random.randint(0,self.tableWidget.columnCount())
		laY=random.randint(0,self.tableWidget.rowCount())
		corCabeza = [laY,laX]
		corCuerpo1 = [laY,(laX-1) % self.tableWidget.columnCount()]
		corCuerpo2 = [laY,(laX-2) % self.tableWidget.columnCount()]
		corCuerpo3 = [laY, (laX-3) % self.tableWidget.columnCount()]
		corCola = [laY,(laX-4) % self.tableWidget.columnCount()]
		return [corCabeza[0],corCabeza[1],corCuerpo1[0],corCuerpo1[1],corCuerpo2[0],corCuerpo2[1],corCuerpo3[0],corCuerpo3[1],corCola[0],corCola[1]]

#Dado a que las vivoras tienen propiedades como color y id. Se crea una clase que le de a sus objetos, dichos atributos.
class Vivora():
	id = None
	color = []
	coordenadas = []
	direccion = 0
	cabezaSnake = QTableWidgetItem()
	cuerpoSnake1 = QTableWidgetItem()
	cuerpoSnake2 = QTableWidgetItem()
	cuerpoSnake3 = QTableWidgetItem()
	colaSnake = QTableWidgetItem()

	#Se crea una serpiente para añadirla posteriormente al juego
	def __init__(self, id, color, coordenadas, direccion):
		self.id = id
		self.color = [color[0],color[1],color[2]]
		self.coordenadas = coordenadas
		self.direccion = direccion
		self.cabezaSnake.setBackgroundColor(QtGui.QColor(color[0],color[1],color[2]))
		self.cuerpoSnake1.setBackgroundColor(QtGui.QColor(color[0],color[1],color[2]))
		self.cuerpoSnake2.setBackgroundColor(QtGui.QColor(color[0],color[1],color[2]))
		self.cuerpoSnake3.setBackgroundColor(QtGui.QColor(color[0],color[1],color[2]))
		self.colaSnake.setBackgroundColor(QtGui.QColor(color[0],color[1],color[2]))

	def todenuevo(self):
		self.cabezaSnake = QTableWidgetItem()
		self.cuerpoSnake1 = QTableWidgetItem()
		self.cuerpoSnake2 = QTableWidgetItem()
		self.cuerpoSnake3 = QTableWidgetItem()
		self.colaSnake = QTableWidgetItem()
		self.cabezaSnake.setBackgroundColor(QtGui.QColor(self.color[0],self.color[1],self.color[2]))
		self.cuerpoSnake1.setBackgroundColor(QtGui.QColor(self.color[0],self.color[1],self.color[2]))
		self.cuerpoSnake2.setBackgroundColor(QtGui.QColor(self.color[0],self.color[1],self.color[2]))
		self.cuerpoSnake3.setBackgroundColor(QtGui.QColor(self.color[0],self.color[1],self.color[2]))
		self.colaSnake.setBackgroundColor(QtGui.QColor(self.color[0],self.color[1],self.color[2]))

#Inicia la aplicacion.
def main():
	app = QtGui.QApplication(sys.argv)
	win = Servidor()
	win.show()
	app.exec_()
	
main()
