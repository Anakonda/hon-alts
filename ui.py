import zipfile
import os
import sys

import data
import hero
import settings

import PyQt5
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

DEFAULT = "default behaviour"

class ListItem(QtWidgets.QListWidgetItem):
	def __init__(self, entityname):
		if entityname + "_name" in data.translations:
			self.displayname = data.translations[entityname + "_name"]
		else:
			self.displayname = entityname
		QtWidgets.QListWidgetItem.__init__(self, self.displayname)
		self.selectedAlt = DEFAULT
		self.entityname = entityname
		try:
			self.hero = hero.Hero(data.heroes[entityname][0], data.heroes[entityname][1])
		except Exception as e:
			print("Failed to parse hero {hero} from file {file}".format(hero=self.displayname, file=data.heroes[entityname][1]))
			type, value, traceback = sys.exc_info()
			print(type.__name__, value)


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)
		self.resize(500, 300)
		self.setWindowTitle("Hon alt tool")

		self.draw()

		self.show()

	def draw(self):
		self.cwidget = QtWidgets.QWidget()
		layout = QtWidgets.QHBoxLayout(self.cwidget)
		self.herolist = QtWidgets.QListWidget(self.cwidget)
		self.herolist.setSortingEnabled(True)
		for entityname in data.heroes.keys():
			item = ListItem(entityname)
			if entityname in settings.selectedAlts:
				item.selectedAlt = settings.selectedAlts[entityname]
			self.herolist.addItem(item)
		self.herolist.currentItemChanged.connect(self.heroChanged)
		self.herolist.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
		self.altlist = QtWidgets.QListWidget(self.cwidget)
		self.altlist.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
		self.altlist.currentItemChanged.connect(self.altChanged)
		layout.addWidget(self.herolist)
		layout.addWidget(self.altlist)

		self.setCentralWidget(self.cwidget)

		exitAction = QtWidgets.QAction("&Exit", self)
		exitAction.setShortcut("Ctrl+Q")
		exitAction.setStatusTip("Exit application")
		exitAction.triggered.connect(QtWidgets.qApp.quit)

		generateAction = QtWidgets.QAction("&Generate", self)
		generateAction.setShortcut("Ctrl+S")
		generateAction.setShortcut("Generate the mod")
		generateAction.triggered.connect(self.generate)

		menubar = self.menuBar()
		fileMenu = menubar.addMenu("&File")
		fileMenu.addAction(generateAction)
		fileMenu.addAction(exitAction)

		defaultAll = QtWidgets.QAction("default", self)
		defaultAll.triggered.connect(self.defaultAll)
		selectMenu = menubar.addMenu("Select")
		selectMenu.addAction(defaultAll)

	def heroChanged(self, new, previous):
		items = [DEFAULT, "default alt"] + new.hero.getAlts()
		self.altlist.clear()
		self.altlist.addItems(items)
		self.altlist.setCurrentItem(self.altlist.findItems(new.selectedAlt, QtCore.Qt.MatchExactly)[0])

	def altChanged(self, new, previous):
		if new is None:
			return
		self.herolist.currentItem().selectedAlt = new.text()

	def generate(self, checked):
		modzip = zipfile.ZipFile(os.path.join(settings.honpath, "game/resourcesAutomaticAlts.s2z"), "w")
		settings.selectedAlts = dict()
		for i in range(self.herolist.count()):
			item = self.herolist.item(i)
			if item.selectedAlt != DEFAULT:
				settings.selectedAlts[item.entityname] = item.selectedAlt
				for filename, content in item.hero.generate(item.selectedAlt).items():
					if content is not None:
						modzip.writestr(filename, content)
		modzip.close()

		settingsfile = open(settings.__file__, "w")
		settingsfile.write("honpath = '")
		settingsfile.write(settings.honpath)
		settingsfile.write("'\n\nselectedAlts = ")
		settingsfile.write(str(settings.selectedAlts))
		settingsfile.write("\n")
		settingsfile.close()

		print("Generating done")

	def defaultAll(self, checked):
		for i in range(self.herolist.count()):
			self.herolist.item(i).selectedAlt = DEFAULT
		self.altlist.setCurrentItem(self.altlist.findItems(DEFAULT, QtCore.Qt.MatchExactly)[0])
