import urllib2 as urllib
import signal
import giphypop
import sys
import tempfile
from PyQt4 import QtGui
from PyQt4.QtCore import *

class GetGiphyLineEdit(QtGui.QLineEdit):
	def __init__(self):
		self.ctrl = False
		super(GetGiphyLineEdit, self).__init__()

	def keyPressEvent(self, event):
		if event.modifiers() == Qt.ControlModifier:
			self.ctrl = True
		
		if event.key() == Qt.Key_C and self.ctrl == True:
			self.emit(SIGNAL("CopyAndQuit"))

		super(GetGiphyLineEdit, self).keyPressEvent(event)

	def keyReleaseEvent(self, event):
		if event.modifiers() == Qt.ControlModifier:
			self.ctrl = False
		super(GetGiphyLineEdit, self).keyReleaseEvent(event)

class GiphyRetriever(QObject):

	# url
	retrieve = pyqtSignal(str)
	# Filename
	finishedRetrieve = pyqtSignal(str)

	def __init__(self):
		super(self.__class__, self).__init__()
		self.retrieve.connect(self.RetrieveGiphy)

	@pyqtSlot(str)
	def RetrieveGiphy(self, url):
		print "Retrieving url " + str(url)
		url = str(url)
		netGiphy = urllib.urlopen(url)
		self.tempFile = tempfile.NamedTemporaryFile(mode="wb")
		while True:
			chunk = netGiphy.read(4096)
			if not chunk: break
			self.tempFile.write(chunk)

		self.finishedRetrieve.emit(self.tempFile.name)

class GetGiphyWidget(QtGui.QWidget):

	def __init__(self):
		super(GetGiphyWidget, self).__init__()

		searchInputOk = QtGui.QPushButton("Next")
		searchInputOk.clicked.connect(self.GetNextGiphy)

		doneBtn = QtGui.QPushButton("Done")
		doneBtn.clicked.connect(self.CopyToClipboardAndExit)

		self.giphySearchInput = GetGiphyLineEdit()
		self.giphySearchInput.setAlignment(Qt.AlignHCenter)
		self.giphySearchInput.returnPressed.connect(searchInputOk.click)
		self.connect(self.giphySearchInput, SIGNAL("CopyAndQuit"), self.CopyToClipboardAndExit)

		self.gifViewerMovie = QtGui.QMovie()
		self.gifViewerScreen = QtGui.QLabel()
		self.gifViewerScreen.setMovie(self.gifViewerMovie)

		buttonLayout = QtGui.QHBoxLayout()
		buttonLayout.addWidget(searchInputOk)
		buttonLayout.addWidget(doneBtn)

		layout = QtGui.QVBoxLayout()
		layout.addWidget(self.gifViewerScreen)
		layout.addWidget(self.giphySearchInput)
		layout.addLayout(buttonLayout)

		self.giphy = giphypop.Giphy()
		self.term = ""

		self.giphyRetrieverThread = QThread()
		self.giphyRetrieverThread.start()

		self.giphyRetriever = GiphyRetriever()
		self.giphyRetriever.moveToThread(self.giphyRetrieverThread)
		self.giphyRetriever.finishedRetrieve.connect(self.DisplayGiphy)

		self.setLayout(layout)
		self.show()

	def RetrieveGiphyList(self):
		term = self.giphySearchInput.text()
		if self.term != term:
			self.term = str(term)
			self.searchResults = self.giphy.search(term=self.term, limit=25)

	def GetNextGiphy(self):
		self.RetrieveGiphyList()
		self.QueueRetrieveNextGiphy()

	def QueueRetrieveNextGiphy(self):
		try:
			self.currentGiphy = self.searchResults.next()
			self.giphyRetriever.retrieve.emit(self.currentGiphy.fixed_width.url)
		except StopIteration:
			print "no more"


	def DisplayGiphy(self, fileName):
		self.gifViewerMovie = QtGui.QMovie(fileName)
		self.gifViewerScreen.setMovie(self.gifViewerMovie)
		self.gifViewerMovie.start()

	def CopyToClipboardAndExit(self):
		if self.currentGiphy == None:
			self.RetrieveGiphyList()
			self.currentGiphy = self.searchResults.next().media_url
		clipboard = QtGui.QApplication.clipboard()
		clipboard.setText(self.currentGiphy.media_url)
		QtGui.QApplication.closeAllWindows()
	
	def closeEvent(self, event):
		self.giphyRetrieverThread.quit()
		self.giphyRetrieverThread.wait()
		super(self.__class__, self).closeEvent(event)

	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Escape:
			self.close()
		super(self.__class__, self).keyPressEvent(e)

def run():
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	app = QtGui.QApplication(sys.argv)
	giphyWidget = GetGiphyWidget()
	sys.exit(app.exec_())

