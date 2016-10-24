import sys
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import random
import uuid

#Se carga la interfaz de tipo ui del servidor
servidorUi = uic.loadUiType("servidor2.ui")[0]
 
class Servidor(QtGui.QMainWindow, servidorUi):

	#Constructor de la ventana
	def __init__(self, parent=None):
		QtGui.QMainWindow.__init__(self, parent)
		self.setupUi(self)#Inicializa la interfaz del tipo ui

		#Estira las celdas para ocupar todo el widget, además desaparece las scrollbar
		self.tableWidget.horizontalHeader().setResizeMode(QHeaderView.Stretch) 
		self.tableWidget.verticalHeader().setResizeMode(QHeaderView.Stretch) 
		self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
		self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 

		
		self.columnas.setMinimum(10) 
		self.columnas.valueChanged.connect(self.ajustaColumnas) 

		#Cantidad minima de renglones de widget y actualiza las mismas con valores de la spinbox
		self.filas.setMinimum(10) 
		self.filas.valueChanged.connect(self.ajustaRenglones)

		#TIMER que ejecuta la funcion cierta cantidad de tiempo
		self.espera.setMaximum(999)
		self.espera.setMinimum(10)
		self.espera.setValue(150)
		self.espera.valueChanged.connect(self.speed) 

		#Tiempo que espera el servidor una accion(con esto no se congela)
		self.timeout.valueChanged.connect(self.update)

		#Inicia columnas y renglones 
		self.tableWidget.setColumnCount(self.columnas.value()) 
		self.tableWidget.setRowCount(self.filas.value()) 
		
		#Controlador de la snake 
		self.tableWidget.keyPressEvent = self.keyPressEvent

		#Botones funcionales
		self.iniciajuego.clicked.connect(self.playGameButton)
		self.pushButton_2.clicked.connect(self.termina)
		self.pushButton_2.hide()
		self.serverstart.clicked.connect(self.sirve)
		
		#Lista de serpientes(Objetos)
		self.misViboras=[]

		#Lista de serpientes(Atributos de objetos)
		self.misViborasInfo= []
		

	#Cambia las columnas cuando se cambia el valor de la spinbox
	def ajustaColumnas(self, columnas): 
		self.tableWidget.setColumnCount(columnas)

 	#Cambia las filas cuando se cambia el valor de la spinbox
	def ajustaRenglones(self, renglones):
		self.tableWidget.setRowCount(renglones)

	#Tiempo que se espera para ejecutar una funcion
	def speed(self, velocidad):
		self.timer.setInterval(velocidad)

	#Checa si la vibora choco con su cola
	def matame(self, bibora):
		if bibora.coordenadas[1] == bibora.coordenadas[9] and bibora.coordenadas[0] == bibora.coordenadas[8]:
			return True

	#Inicia el juego
	def playGameButton(self):
		if self.iniciajuego.text() == "Inicia Juego":
			self.snake = self.snakeMaker()
			self.iniciajuego.setText("Pausar el juego")

			self.pushButton_2.show()

			#Inicia al timer que ejecutara la funcion para que la vibora se mueva
			self.timer = QTimer()
			self.timer.timeout.connect(self.mueve)
			self.timer.start(150)

			self.espera.setValue(150)

		#Detiene el timer, osea detiene la funcion que mueve a la serpiente
		elif self.iniciajuego.text() == "Pausar el juego":
			self.timer.stop()
			self.iniciajuego.setText("Reanudar juego")

		#Espera el tiempo que la spinbox le diga para ejecutar la funcion
		else: 
			self.timer.start(self.espera.value())
			self.iniciajuego.setText("Pausar el juego")
 
	#Borra a la serpiente y despues la crea con una todas sus partes una unidad a la derecha (adicion)
	#Esto se repite n veces, por lo cual va asociado al timer
	def caminaDerecha(self,bibora):

		self.desaparece(bibora)
		bibora.coordenadas[8], bibora.coordenadas[9] = bibora.coordenadas[6], bibora.coordenadas[7]
		bibora.coordenadas[6], bibora.coordenadas[7] = bibora.coordenadas[4], bibora.coordenadas[5]
		bibora.coordenadas[4], bibora.coordenadas[5] = bibora.coordenadas[2], bibora.coordenadas[3]
		bibora.coordenadas[2], bibora.coordenadas[3] = bibora.coordenadas[0], bibora.coordenadas[1]
		bibora.coordenadas[0], bibora.coordenadas[1] = bibora.coordenadas[0], (bibora.coordenadas[1] + 1)% self.tableWidget.columnCount()
		bibora.direccion = 1
		bibora.existeDenuevo()
		self.aparece(bibora)

	#Borra a la serpiente y la rehace con sus partes una unidad a la izquierda (sustraccion)
	#Asociado timer
	def caminaIzquierda(self,bibora):

		self.desaparece(bibora)
		bibora.coordenadas[8], bibora.coordenadas[9] = bibora.coordenadas[6], bibora.coordenadas[7]
		bibora.coordenadas[6], bibora.coordenadas[7] = bibora.coordenadas[4], bibora.coordenadas[5]
		bibora.coordenadas[4], bibora.coordenadas[5] = bibora.coordenadas[2], bibora.coordenadas[3]
		bibora.coordenadas[2], bibora.coordenadas[3] = bibora.coordenadas[0], bibora.coordenadas[1]
		bibora.coordenadas[0], bibora.coordenadas[1] = bibora.coordenadas[0], (bibora.coordenadas[1] - 1)% self.tableWidget.columnCount()
		bibora.direccion = 3
		bibora.existeDenuevo()
		self.aparece(bibora)

	#Borra a la serpiente y la rehace con sus partes una unidad hacia arriba (renglones sustraccion)
	#Asociado timer
	def caminaArriba(self,bibora):

		self.desaparece(bibora)
		bibora.coordenadas[8], bibora.coordenadas[9] = bibora.coordenadas[6], bibora.coordenadas[7]
		bibora.coordenadas[6], bibora.coordenadas[7] = bibora.coordenadas[4], bibora.coordenadas[5]
		bibora.coordenadas[4], bibora.coordenadas[5] = bibora.coordenadas[2], bibora.coordenadas[3]
		bibora.coordenadas[2], bibora.coordenadas[3] = bibora.coordenadas[0], bibora.coordenadas[1]
		bibora.coordenadas[0], bibora.coordenadas[1] = (bibora.coordenadas[0]-1)%self.tableWidget.rowCount(), bibora.coordenadas[1] 
		bibora.direccion = 0
		bibora.existeDenuevo()
		self.aparece(bibora)

	#Borra a la serpiente y la rehace con sus partes una unidad hacia abajo (renglones adicion)
	#Asociado timer
	def caminaAbajo(self,bibora):

		self.desaparece(bibora)
		bibora.coordenadas[8], bibora.coordenadas[9] = bibora.coordenadas[6], bibora.coordenadas[7]
		bibora.coordenadas[6], bibora.coordenadas[7] = bibora.coordenadas[4], bibora.coordenadas[5]
		bibora.coordenadas[4], bibora.coordenadas[5] = bibora.coordenadas[2], bibora.coordenadas[3]
		bibora.coordenadas[2], bibora.coordenadas[3] = bibora.coordenadas[0], bibora.coordenadas[1]
		bibora.coordenadas[0], bibora.coordenadas[1] = (bibora.coordenadas[0]+1)%self.tableWidget.rowCount(), bibora.coordenadas[1] 
		bibora.direccion = 2
		bibora.existeDenuevo()
		self.aparece(bibora)

	#Mueve a la vibora segun su direccion una cantidad infinita de veces
	def condicional(self, bibora):
		if bibora.direccion == 0:
			self.caminaArriba(bibora)
		elif bibora.direccion == 1:
			self.caminaDerecha(bibora)
		elif bibora.direccion == 2:
			self.caminaAbajo(bibora)
		elif bibora.direccion == 3:  
			self.caminaIzquierda(bibora)
		if self.matame(bibora):
			self.termina(bibora)

	#Unicamente para que la serpiente del servidor se mueva
	def mueve(self):
		self.condicional(self.snake)

	#De nuevo unicamente mueve a la serpiente que funciona solo en el servidor
	def keyPressEvent(self,event):
		if event.key() == QtCore.Qt.Key_Left and self.snake.direccion != 1:
			self.snake.direccion= 3
		elif event.key() == QtCore.Qt.Key_Right and self.snake.direccion != 3:
			self.snake.direccion= 1
		elif event.key() == QtCore.Qt.Key_Up and self.snake.direccion != 2:
			self.snake.direccion= 0
		elif event.key() == QtCore.Qt.Key_Down and self.snake.direccion != 0:
			self.snake.direccion= 2
	
	#Borra la widget, detiene el timer, borra las listas de serpientes y da oportunidad de nuevo juego
	def termina(self, bibora):
		self.timer.stop()
		self.tableWidget.clear()
		self.misViboras.clear()
		self.misViborasInfo.clear()
		self.iniciajuego.setText("Inicia Juego")
		self.pushButton_2.hide()

	#Inicia el servidor
	def sirve(self):
		if self.puerto.value()==0:
			self.servidor = SimpleXMLRPCServer((self.url.text(), 8000), allow_none= True) 
			self.puerto.setValue(8000)
		else:
			self.servidor = SimpleXMLRPCServer((self.url.text(), self.puerto.value()), allow_none= True)

		self.servidor.timeout = self.timeout.value()
		self.servidor.register_function(self.ping)
		self.servidor.register_function(self.yo_juego)
		self.servidor.register_function(self.estado_del_juego)
		self.servidor.register_function(self.camba_direccion)
		self.servidor.register_function(self.dameMiViboraInfo)
		self.servidor.register_function(self.dameMiViboraId)

		#Hace esperar al servidor solo un tiempo limitado
		self.krusty= QTimer(self)
		self.krusty.timeout.connect(self.cliente)
		self.krusty.start(100)

		#Solo se puede iniciar el server una vez
		self.serverstart.hide()

	#Le da al servidor un numero que representa el tiempo de espera
	def update(self, cuanto):
		self.servidor.timeout = cuanto

	#Así como en el ejemplo esta funcion va a escuchar por una llamada del cliente, si la escucha regresara una funcion
	def cliente(self):
		self.servidor.handle_request()

	#Metodo que regresa un pong por cada ping
	def ping(self):
		return "¡Pong!"

	#metodo que devuelve las propiedades de la vibora
	def yo_juego(self):
		vivora = self.snakeMaker()
		self.aparece(vivora)
		return {"id": vivora.id, "color": {"r": vivora.color[0], "g": vivora.color[1], "b": vivora.color[2]}}

	#Cambia la direccion de la serpiente que esta en el cliente
	def camba_direccion(self,identificador,direccioname):
		serpienteEncontrada = dameMiViboraId(identificador)
		if serpienteEncontrada != None:
			serpienteEncontrada.direccion = direccioname

	#Regresa como es que se ve el juego, en la llamada
	def estado_del_juego(self):
		return {"espera": self.espera.value(), "tamX": self.tableWidget.columnCount(), "tamY": self.tableWidget.rowCount(), "vivoras":self.misViborasInfo}


	#Creamos el objeto vivora y le damos atributos aleatorios
	def snakeMaker(self):
		identificacion = self.identificacionUnica()
		color = self.coloresRandom()
		coordenadas = self.coordenadasRandom()
		direccion = random.randint(0,3)
		vivora = Vivora(identificacion,color,coordenadas,direccion)
		self.misViboras.append(vivora)
		self.misViborasInfo.append({"id": id, "camino": coordenadas, "color": color})
		self.aparece(vivora)
		return vivora

	#Busca al objeto vibora poseedora de esa id, regresa las propiedades de dicha (Para poderla pintar en el servidor y cliente)
	def dameMiViboraInfo(self, identify):
		esEsta = None
		for i in range(len(self.misViborasInfo)):
			if self.misViborasInfo[i]['id'] == identify:
				esEsta = self.misViborasInfo[i]
		return esEsta

	#Regresa al objeto vibora poseedora de esa identificacion
	def dameMiViboraId(self,credencial):
		laVibora = None
		for i in range(len(self.misViboras)):
			if str(self.misViboras[i].id) == credencial:
				laVibora = self.misViboras[i]
		return laVibora

	#Le da a la widget items donde estara la vibora, las coordenadas ya las tiene el objeto vibora
	def aparece(self,bibora):
		self.tableWidget.setItem(bibora.coordenadas[0], bibora.coordenadas[1], bibora.cabezaSnake)
		self.tableWidget.setItem(bibora.coordenadas[2], bibora.coordenadas[3], bibora.cuerpoSnake1)
		self.tableWidget.setItem(bibora.coordenadas[4], bibora.coordenadas[5], bibora.cuerpoSnake2)
		self.tableWidget.setItem(bibora.coordenadas[6], bibora.coordenadas[7], bibora.cuerpoSnake3)
		self.tableWidget.setItem(bibora.coordenadas[8], bibora.coordenadas[9], bibora.colaSnake)

	#Inversa de aparece
	def desaparece(self,bibora):
		self.tableWidget.takeItem(bibora.coordenadas[0], bibora.coordenadas[1])
		self.tableWidget.takeItem(bibora.coordenadas[2], bibora.coordenadas[3])
		self.tableWidget.takeItem(bibora.coordenadas[4], bibora.coordenadas[5])
		self.tableWidget.takeItem(bibora.coordenadas[6], bibora.coordenadas[7])
		self.tableWidget.takeItem(bibora.coordenadas[8], bibora.coordenadas[9]) 

	#Dada la exigencia, crea una lista de colores que va de r,g,b y oscila entre 0 y 255, rango de colores de python
	def coloresRandom(self):
		r = random.randint(0,255)
		g = random.randint(0,255)
		b = random.randint(0,255)

		return [r,g,b]

	#Le asigna in id unico a la vibora
	def identificacionUnica(self):
		return str(uuid.uuid4())

	#Crea lista de coordenadas random para la serpiente
	def coordenadasRandom(self):
		laX=random.randint(0,self.tableWidget.columnCount())
		laY=random.randint(0,self.tableWidget.rowCount())
		corCabeza = [laY,laX]
		corCuerpo1 = [laY,((laX-1) % self.tableWidget.columnCount())]
		corCuerpo2 = [laY,((laX-2) % self.tableWidget.columnCount())]
		corCuerpo3 = [laY, ((laX-3) % self.tableWidget.columnCount())]
		corCola = [laY,((laX-4) % self.tableWidget.columnCount())]
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

	#Vuelve a crear todos las partes de la vibora
	def existeDenuevo(self):
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
