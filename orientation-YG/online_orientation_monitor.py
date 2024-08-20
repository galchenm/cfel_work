#!/usr/bin/env python3
# coding: utf8

from PyQt5 import QtCore, QtWidgets, QtGui
import numpy as np
import pyqtgraph as pg
import time
import sys
import click
from sortedcontainers import SortedDict
import re
import pyqtgraph.opengl as gl

markerSize = 0.5


class StreamReader(QtCore.QObject):
    data = QtCore.pyqtSignal(dict)

    def __init__(self, filename):
        QtCore.QObject.__init__(self)
        self.filename = filename
        self._stream = None
        self._is_running = True

    def read_stream(self):
        while self._stream is None and self._is_running is True:
            try:
                self._stream = open(self.filename, "r")
            except FileNotFoundError:
                print("File {} not found, waiting...".format(self.filename))
                time.sleep(1)

        while self._stream is not None and self._is_running is True:
            line = self._stream.readline()
            if not line:
                time.sleep(0.1)
                continue

            elif line.startswith("--- Begin crystal"):
                timestamp = None
                indexed = False

            elif line.startswith("header/float/timestamp"):
                timestamp = float(line.split()[-1])
                
            elif line.startswith("astar = "):
                
                p = re.compile("astar = ([\+\-\d\.]* [\+\-\d\.]* [\+\-\d\.]*)")
                xStarStrings = p.findall(line)
                aStars = np.zeros((len(xStarStrings),3), float)
                for j in np.arange(len(xStarStrings)):
                    aStars[j,:] = np.array([float(s) for s in xStarStrings[j].split(' ')])
                                    
            elif line.startswith("bstar = "):
                p = re.compile("bstar = ([\+\-\d\.]* [\+\-\d\.]* [\+\-\d\.]*)")
                xStarStrings = p.findall(line)
                bStars = np.zeros((len(xStarStrings),3), float)
                for j in np.arange(len(xStarStrings)):
                    bStars[j,:] = np.array([float(s) for s in xStarStrings[j].split(' ')])
                    
            elif line.startswith("cstar = "):
                p = re.compile("cstar = ([\+\-\d\.]* [\+\-\d\.]* [\+\-\d\.]*)")
                xStarStrings = p.findall(line)
                cStars = np.zeros((len(xStarStrings),3), float)
                for j in np.arange(len(xStarStrings)):
                    cStars[j,:] = np.array([float(s) for s in xStarStrings[j].split(' ')])  
                indexed = True
                
            elif line.startswith("--- End crystal"):
                if not indexed:
                    continue
                if timestamp is None:
                    timestamp = time.time()
                self.data.emit({
                    "timestamp": timestamp, 
                    "astar": aStars, 
                    "bstar": bStars, 
                    "cstar": cStars
                })

    def stop(self):
        self._is_running = False


class CellExplorerGui(QtWidgets.QMainWindow):
    """ """
    def __init__(self, stream_filename):
        """ """
        super(CellExplorerGui, self).__init__()
        pg.setConfigOption('background', 'k')
        pg.setConfigOption('foreground', 'k')
        
        self._stream_filename = stream_filename

        self._refresh_timer = QtCore.QTimer()
        self._refresh_timer.timeout.connect(self._update_gui)
        self._refresh_timer.start(500)

        self.setWindowTitle("Online orientation monitor")
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(layout)
        self.resize(1000, 800)
        
        
        self._plots_widget = pg.GraphicsWindow(title="Online orientation monitor")
        
        layout.addWidget(self._plots_widget)

        self._delay_widget = QtWidgets.QLabel()
        layout.addWidget(self._delay_widget)

        self._buttons_widget = QtWidgets.QWidget()
        layout.addWidget(self._buttons_widget)

        buttons_layout = QtWidgets.QHBoxLayout()
        self._buttons_widget.setLayout(buttons_layout)

        self._clear_data_button = QtWidgets.QPushButton()
        self._clear_data_button.setText("Clear data")
        self._clear_data_button.clicked.connect(self._clear_data)
        buttons_layout.addWidget(self._clear_data_button)

        self._reload_stream_button = QtWidgets.QPushButton()
        self._reload_stream_button.setText("Reload stream")
        self._reload_stream_button.clicked.connect(self._reload_stream)
        buttons_layout.addWidget(self._reload_stream_button)

        self._log_widget = QtWidgets.QTextEdit()
        self._log_widget.setMaximumHeight(150)
        self._log_widget.setReadOnly(True)
        self._log_widget.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        layout.addWidget(self._log_widget)
               
        self._astar_widget = gl.GLViewWidget()
        self._astar_widget.setWindowTitle('a*')
        self._astar_widget.opts['distance'] = 0.4
        #self._astar_widget.setBackgroundColor('w')
        self._sp1 = gl.GLScatterPlotItem(pos=np.array([0,0,0]),color=(1.0,0,0,0.5), size=markerSize)
        
        self._sp1.setGLOptions('translucent')
        self._astar_widget.addItem(self._sp1)
        
        self._bstar_widget = gl.GLViewWidget()
        self._bstar_widget.opts['distance'] = 0.4 
        #self._bstar_widget.setBackgroundColor('w')
        self._sp2 = gl.GLScatterPlotItem(pos=[], color=(0.,1.0,0,0.5), size=markerSize)
        
        self._sp2.setGLOptions('translucent')
        self._bstar_widget.addItem(self._sp2)
        
        self._cstar_widget = gl.GLViewWidget()
        #self._cstar_widget.setBackgroundColor('w')
        self._cstar_widget.opts['distance'] = 0.4 
        self._sp3 = gl.GLScatterPlotItem(pos=[], color=(1.0,0.0,1.0,0.5), size=markerSize)
        
        self._sp3.setGLOptions('translucent')
        self._cstar_widget.addItem(self._sp3)
                
        self._layoutgb = QtGui.QGridLayout()
        self._plots_widget.setLayout(self._layoutgb)
        
        self._layoutgb.addWidget(self._astar_widget, 0, 0)
        self._layoutgb.addWidget(self._bstar_widget, 0, 1)
        self._layoutgb.addWidget(self._cstar_widget, 0, 2)
        
        self._astar_widget.sizeHint = lambda: pg.QtCore.QSize(700, 500)
        self._bstar_widget.sizeHint = lambda: pg.QtCore.QSize(700, 500)
        self._cstar_widget.sizeHint = lambda: pg.QtCore.QSize(700, 500)
        
        self._astar_widget.setSizePolicy(self._bstar_widget.sizePolicy())
        self._astar_widget.setSizePolicy(self._cstar_widget.sizePolicy())
        
        self._data = SortedDict()
        self._num_cells = 0
        self._start_stream_reader()

    def _start_stream_reader(self):
        self._stream_reader_thread = QtCore.QThread(parent=self)
        self._stream_reader = StreamReader(self._stream_filename)
        self._stream_reader.moveToThread(self._stream_reader_thread)
        self._stream_reader_thread.started.connect(self._stream_reader.read_stream)
        self._stream_reader.data.connect(self._update_data)
        self._stream_reader_thread.start()

    def _stop_stream_reader(self):
        self._stream_reader.stop()
        self._stream_reader_thread.quit()

    def _clear_data(self):
        self._data = SortedDict()

    def _reload_stream(self):
        self._stop_stream_reader()
        self._start_stream_reader()

    def _write_to_log(self, text):
        self._log_widget.moveCursor(QtGui.QTextCursor.End)
        self._log_widget.insertPlainText(text)
        sb = self._log_widget.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _update_data(self, data):
        self._data[data["timestamp"]] = data
        astars_line = " ".join(list(map(str, data["astar"][0])))
        bstars_line = " ".join(list(map(str, data["bstar"][0])))
        cstars_line = " ".join(list(map(str, data["cstar"][0])))
        self._write_to_log(f'astars = {astars_line} nm^-1; bstars = {bstars_line} nm^-1; cstars = {cstars_line} nm^-1\n')

    def _update_gui(self):
        n = len(self._data)
        
        astar_values = np.array([data["astar"][0] for data in self._data.values()])
        self._sp1.setData(pos=astar_values,color=(1.0,0,0,0.5),size=markerSize)
        
        bstar_values = np.array([data["bstar"][0] for data in self._data.values()])
        self._sp2.setData(pos=bstar_values,color=(0.,1.0,0,0.5),size=markerSize)
        
        cstar_values = np.array([data["cstar"][0] for data in self._data.values()])
        self._sp3.setData(pos=cstar_values,color=(1.0,0.0,1.0,0.5),size=markerSize)



@click.command()
@click.argument("stream", type=str, required=True)
def main(stream):
    app = QtWidgets.QApplication(sys.argv)
    win = CellExplorerGui(stream)
    win.show()
    sys.exit(app.exec_())    


if __name__ == '__main__':
    main()
