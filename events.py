# Simple example which will print out every Qt event
# that is received by a window.  It'll give you a hint
# about which Event type to look up in the docs.


import sys
from PyQt4 import QtGui, QtCore

class Example(QtGui.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        
        # self.initUI()
        
    def initUI(self):      
        
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Event handler')
        self.show()
        
    def event(self, evt):
      print evt
      return True
        
    def keyPressEvent(self, e):
        
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
            
            
            
app = QtGui.QApplication(sys.argv)
ex = Example()
sys.exit(app.exec_())