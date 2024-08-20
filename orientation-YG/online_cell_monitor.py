#!/usr/bin/env python

from PyQt5 import QtCore, QtWidgets, QtGui
import numpy as np
import pyqtgraph as pg
import time
import sys
import click
from sortedcontainers import SortedDict


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

            elif line.startswith("----- Begin chunk -----"):
                timestamp = None
                indexed = False

            elif line.startswith("header/float/timestamp"):
                timestamp = float(line.split()[-1])
                
            elif line.startswith("Cell parameters"):
                indexed = True
                cell = [float(i) for i in line.split()[2:9] if i[0] != "n"]
                # Convert a, b, c to Angstrom:
                for i in range(3):
                    cell[i] *= 10

            elif line.startswith("centering"):
                centering = line.split()[-1].strip()

            elif line.startswith("diffraction_resolution_limit"):
                resolution = float(line.split()[-2])

            elif line.startswith("----- End chunk"):
                if not indexed:
                    continue
                if timestamp is None:
                    timestamp = time.time()
                self.data.emit({
                    "timestamp": timestamp, 
                    "cell": cell, 
                    "centering": centering,
                    "resolution": resolution,
                })

    def stop(self):
        self._is_running = False


class CellExplorerGui(QtWidgets.QMainWindow):
    """ """
    def __init__(self, stream_filename):
        """ """
        super(CellExplorerGui, self).__init__()
        self._stream_filename = stream_filename

        self._refresh_timer = QtCore.QTimer()
        self._refresh_timer.timeout.connect(self._update_gui)
        self._refresh_timer.start(500)

        self.setWindowTitle("Unit cell monitor")
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(layout)
        self.resize(1000, 800)

        #self._plots_widget = pg.GraphicsLayoutWidget(show=True)
        self._plots_widget = pg.GraphicsLayoutWidget()
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

        self._plots = []
        self._plots.append(self._plots_widget.addPlot(name="0", title="a"))
        self._plots.append(self._plots_widget.addPlot(name="1", title="b"))
        self._plots.append(self._plots_widget.addPlot(name="2", title="c"))

        self._plots_widget.nextRow()

        self._plots.append(self._plots_widget.addPlot(name="3", title="alpha"))
        self._plots.append(self._plots_widget.addPlot(name="4", title="beta"))
        self._plots.append(self._plots_widget.addPlot(name="5", title="gamma"))

        self._ranges = [
            [0, 500],
            [0, 500],
            [0, 500],
            [0, 180],
            [0, 180],
            [0, 180]
        ]

        self._curves = []
        self._curves_latest = []
        for i in range(6):
            self._curves.append(self._plots[i].plot())
            self._curves_latest.append(self._plots[i].plot())
            self._plots[i].setMouseEnabled(x=True, y=False)
            self._plots[i].enableAutoRange(x=False, y=True)
            self._plots[i].sigXRangeChanged.connect(self._update_range)
            self._plots[i].setXRange(*self._ranges[i], padding=0)

        self._curves_parameters = {
            "stepMode": "center", 
            "fillLevel": 0,
            "fillOutline": False,
            "brush": (0,0,255,150),
        }

        self._curves_latest_parameters = {
            "stepMode": "center",
            "fillLevel": 0,
            "fillOutline": False,
            "pen": pg.mkPen(color=(0,255,0,100)),
            "brush": (0,255,0,100),
        }

        legend = pg.LegendItem(offset=(0, 70))
        legend.setParentItem(self._plots[2])
        legend.addItem(self._curves[2], "all cells")
        legend.addItem(self._curves_latest[2], "last 10 cells")

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
        self._write_to_log("{} cell: {:.2f} {:.2f} {:.2f} A, {:.2f} {:.2f} {:.2f} deg, resolution {} A\n".format(
            data["centering"],
            *data["cell"],
            data["resolution"]
        ))

    def _update_gui(self):
        n = len(self._data)
        if n != self._num_cells:
            print("{} indexed".format(n))
        self._num_cells = n

        if n == 0:
            for i in range(6):
                self._curves[i].setData([0, 1], [0], **self._curves_parameters)
                self._curves_latest[i].setData([0, 1], [0], **self._curves_latest_parameters)
            return
        
        timestamp = time.time()
        delay = timestamp - self._data.keys()[-1]
        delay_min = int(delay / 60)
        delay_sec = delay - delay_min * 60
        self._delay_widget.setText("Last indexed event: {} minutes {:.2f} seconds ago".format(delay_min, delay_sec))

        for i in range(6):
            values = [data["cell"][i] for data in self._data.values()]
            #print(len(values))
            y,x = np.histogram(values, bins=30, range=self._ranges[i])
            
            self._curves[i].setData(x, y/y.max(), **self._curves_parameters)

            values = [data["cell"][i] for data in self._data.values()[-10:]]
            y,x = np.histogram(values, bins=90, range=self._ranges[i])
            self._curves_latest[i].setData(x, y/y.max(), **self._curves_latest_parameters)

    def _update_range(self):
        sender = self.sender()
        i = int(sender.getViewBox().name)
        self._ranges[i] = self._plots[i].getViewBox().viewRange()[0]


@click.command()
@click.argument("stream", type=str, required=True)
def main(stream):
    app = QtWidgets.QApplication(sys.argv)
    win = CellExplorerGui(stream)
    win.show()
    sys.exit(app.exec_())    


if __name__ == '__main__':
    main()
