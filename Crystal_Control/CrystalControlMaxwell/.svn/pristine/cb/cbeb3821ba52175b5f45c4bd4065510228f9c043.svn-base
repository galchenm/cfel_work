from PyQt4 import QtCore, QtGui
from eigerThread import EigerThread
import sys
import time
import signal


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
    app = QtGui.QApplication(sys.argv)

    eiger = EigerThread(["p11/eiger/eh.01", "p11/eiger_filewriter/eh.01", "p11/eiger_monitor/eh.01"])
    eiger.start()
    
    time.sleep(2)
    print("1:", eiger.statusEiger)
    print("2:", eiger.triggerMode)
    print("3:", eiger.delayTime)
    print("4:", eiger.imageFilePath)

    eiger.stop()
    
    
    #app.exec_()
