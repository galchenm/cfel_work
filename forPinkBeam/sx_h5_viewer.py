from PyQt5 import QtCore, QtWidgets, QtGui
import pyqtgraph
import click
import h5py
import sys
import numpy
from om.utils import crystfel_geometry
from random import randrange
from scipy import constants


class FrameViewerGui(QtWidgets.QMainWindow):
    """ """

    def __init__(self, input, geometry_filename, hdf5_data_path, hdf5_peaks_path):
        """ """
        super(FrameViewerGui, self).__init__()
        self.statusBar().showMessage("")

        self._geometry, beam, __ = crystfel_geometry.load_crystfel_geometry(
            filename=geometry_filename
        )
        self._pixelmaps = crystfel_geometry.compute_pix_maps(geometry=self._geometry)

        first_panel = list(self._geometry["panels"].keys())[0]
        self._pixel_size = self._geometry["panels"][first_panel]["res"]
        self._clen_from = self._geometry["panels"][first_panel]["clen_from"]
        if self._clen_from == "":
            self._clen = self._geometry["panels"][first_panel]["clen"]
        self._coffset = self._geometry["panels"][first_panel]["coffset"]
        self._photon_energy_from = beam["photon_energy_from"]
        if self._photon_energy_from == "":
            self._photon_energy = beam["photon_energy"]

        if hdf5_data_path is None:
            hdf5_data_path = self._geometry["panels"][first_panel]["data"]
        self._hdf5_data_path = hdf5_data_path

        y_minimum = (
            2
            * int(max(abs(self._pixelmaps["y"].max()), abs(self._pixelmaps["y"].min())))
            + 2
        )
        x_minimum = (
            2
            * int(max(abs(self._pixelmaps["x"].max()), abs(self._pixelmaps["x"].min())))
            + 2
        )
        visual_img_shape = (y_minimum, x_minimum)
        self._img_center_x = int(visual_img_shape[1] / 2)
        self._img_center_y = int(visual_img_shape[0] / 2)
        self._visual_pixelmap_x = (
            numpy.array(self._pixelmaps["x"], dtype=numpy.int)
            + visual_img_shape[1] // 2
            - 1
        ).flatten()
        self._visual_pixelmap_y = (
            numpy.array(self._pixelmaps["y"], dtype=numpy.int)
            + visual_img_shape[0] // 2
            - 1
        ).flatten()

        self._input_files = {}
        self._events = []
        for filename in input:
            self._input_files[filename] = h5py.File(filename, "r")
            data = self._input_files[filename][self._hdf5_data_path]
            if len(data.shape) == 2:
                self._multi_event = False
                self._events.append(filename)
            else:
                self._multi_event = True
                self._events.extend([(filename, i) for i in range(data.shape[0])])

        self._data_shape = (data.shape[-2], data.shape[-1])
        self._frame_data_img = numpy.zeros(visual_img_shape, dtype=data.dtype)
        self._num_events = len(self._events)
        self._current_event = 0
        self._levels_range = [-1000, 10000]
        self._hdf5_peaks_path = hdf5_peaks_path

        pyqtgraph.setConfigOption("background", 0.2)

        self._ring_pen = pyqtgraph.mkPen("r", width=2)
        self._peak_canvas = pyqtgraph.ScatterPlotItem()

        self._image_view = pyqtgraph.ImageView()
        self._image_view.ui.menuBtn.hide()
        self._image_view.ui.roiBtn.hide()
        self._image_view.scene.sigMouseMoved.connect(self._mouse_moved)
        self._image_view.getView().addItem(self._peak_canvas)

        self._values_widget = QtGui.QLabel()

        self._resolution_rings_in_a: List[float] = [
            10.0,
            6.0,
            4.0,
            3.0,
            2.0,
            1.5,
        ]
        self._resolution_rings_textitems: List[Any] = [
            pyqtgraph.TextItem(
                text="{0}A".format(x), anchor=(0.5, 0.8), color=(0, 255, 0)
            )
            for x in self._resolution_rings_in_a
        ]
        self._resolution_rings_enabled: bool = False

        self._received_data: Dict[str, Any] = {}

        pyqtgraph.setConfigOption("background", 0.2)

        self._resolution_rings_pen: Any = pyqtgraph.mkPen("g", width=1)
        self._resolution_rings_canvas: Any = pyqtgraph.ScatterPlotItem()
        self._image_view.getView().addItem(self._resolution_rings_canvas)

        self._resolution_rings_regex: Any = QtCore.QRegExp(r"[0-9.,]+")
        self._resolution_rings_validator: Any = QtGui.QRegExpValidator()
        self._resolution_rings_validator.setRegExp(self._resolution_rings_regex)

        self._resolution_rings_check_box: Any = QtGui.QCheckBox(
            text="Show Resolution Rings", checked=False
        )
        self._resolution_rings_check_box.setEnabled(True)
        self._resolution_rings_lineedit: Any = QtGui.QLineEdit()
        self._resolution_rings_lineedit.setValidator(self._resolution_rings_validator)
        self._resolution_rings_lineedit.setText(
            ",".join(str(x) for x in self._resolution_rings_in_a)
        )
        self._resolution_rings_lineedit.editingFinished.connect(
            self._update_resolution_rings_radii
        )
        self._resolution_rings_lineedit.setEnabled(True)
        self._resolution_rings_check_box.stateChanged.connect(
            self._update_resolution_rings_status
        )
        # Galchenkova
        self._max_box: Any = QtGui.QLineEdit()
        self._min_box: Any = QtGui.QLineEdit()
        self._min_box.setText(str(-1000))
        self._min_box.setMaximumWidth(100)
        self._min_box.move(-100,0)
        self._min_box.setAlignment(QtCore.Qt.AlignCenter)
        self._max_box.setText(str(10000))
        self._max_box.setMaximumWidth(100)
        self._max_box.setAlignment(QtCore.Qt.AlignCenter)
        self._max_box.textChanged.connect(self._onChanged)
        self._min_box.textChanged.connect(self._onChanged)
        self._range_layout = QtGui.QHBoxLayout()
        self._min_label = QtGui.QLabel('Min Int')
        self._min_label.setAlignment(QtCore.Qt.AlignRight| QtCore.Qt.AlignVCenter)
        self._range_layout.addWidget(self._min_label)
        self._range_layout.addWidget(self._min_box)
        self._max_label = QtGui.QLabel('Max Int')
        self._max_label.setAlignment(QtCore.Qt.AlignRight| QtCore.Qt.AlignVCenter)
        self._range_layout.addWidget(self._max_label)
        self._range_layout.addWidget(self._max_box)

        
        ##################################################
        self._back_button = QtGui.QPushButton(text="Back")
        self._back_button.clicked.connect(self._back_button_clicked)

        self._forward_button = QtGui.QPushButton(text="Forward")
        self._forward_button.clicked.connect(self._forward_button_clicked)

        self._random_button: Any = QtGui.QPushButton(text="Random")
        self._random_button.clicked.connect(self._random_button_clicked)

        self._show_peaks_check_box: Any = QtGui.QCheckBox(
            text="Show peaks", checked=False
        )
        if hdf5_peaks_path is None or self._multi_event is False:
            self._show_peaks_check_box.setEnabled(False)
        self._show_peaks_check_box.stateChanged.connect(self._update_peaks)

        self._resolution_rings_layout = QtGui.QHBoxLayout()
        self._resolution_rings_layout.addWidget(self._resolution_rings_check_box)
        self._resolution_rings_layout.addWidget(self._resolution_rings_lineedit)

        self._horizontal_layout: Any = QtGui.QHBoxLayout()
        self._horizontal_layout.addWidget(self._back_button)
        self._horizontal_layout.addWidget(self._forward_button)
        self._horizontal_layout.addWidget(self._random_button)
        self._horizontal_layout.addWidget(self._show_peaks_check_box)
        self._vertical_layout: Any = QtGui.QVBoxLayout()
        self._vertical_layout.addWidget(self._image_view)
        self._vertical_layout.addWidget(self._values_widget)
        self._vertical_layout.addLayout(self._resolution_rings_layout)
        self._vertical_layout.addLayout(self._horizontal_layout)
        
        self._vertical_layout.addLayout(self._range_layout)
        
        self._central_widget: Any = QtGui.QWidget()
        self._central_widget.setLayout(self._vertical_layout)
        self.setCentralWidget(self._central_widget)

        self._update_image_and_peaks()

    def _update_resolution_rings_status(self):
        new_state = self._resolution_rings_check_box.isChecked()
        if self._resolution_rings_enabled is True and new_state is False:
            for text_item in self._resolution_rings_textitems:
                self._image_view.scene.removeItem(text_item)
            self._resolution_rings_canvas.setData([], [])
            self._resolution_rings_enabled = False
        if self._resolution_rings_enabled is False and new_state is True:
            for text_item in self._resolution_rings_textitems:
                self._image_view.getView().addItem(text_item)
            self._resolution_rings_enabled = True
            self._draw_resolution_rings()

    def _update_resolution_rings_radii(self):
        was_enabled = self._resolution_rings_check_box.isChecked()
        self._resolution_rings_check_box.setChecked(False)

        items = str(self._resolution_rings_lineedit.text()).split(",")
        if items:
            self._resolution_rings_in_a = [
                float(item) for item in items if item != "" and float(item) != 0.0
            ]
        else:
            self._resolution_rings_in_a = []

        self._resolution_rings_textitems = [
            pyqtgraph.TextItem(
                text="{0}A".format(x), anchor=(0.5, 0.8), color=(0, 255, 0)
            )
            for x in self._resolution_rings_in_a
        ]
        if was_enabled is True:
            self._resolution_rings_check_box.setChecked(True)
        self._draw_resolution_rings()
    
    #Galchenkova _onChanged
    def _onChanged(self):
        self._levels_range = [float(self._min_box.text()), float(self._max_box.text())]
        self._update_image_and_peaks()
    
    #####################
    
    def _draw_resolution_rings(self):
        # Draws the resolution rings.
        if self._resolution_rings_enabled is False:
            return
        try:
            # TODO: read clen and beam_energy from file if available
            detector_distance = self._clen * 1e3
            photon_energy = self._photon_energy
            lambda_ = constants.h * constants.c / (photon_energy * constants.e)
            resolution_rings_in_pix = [1.0]
            resolution_rings_in_pix.extend(
                [
                    2.0
                    * self._pixel_size
                    * (detector_distance * 1e-3 + self._coffset)
                    * numpy.tan(
                        2.0 * numpy.arcsin(lambda_ / (2.0 * resolution * 1e-10))
                    )
                    for resolution in self._resolution_rings_in_a
                ]
            )
        except:
            print(
                "Beam energy or detector distance information is not available. "
                "Resolution rings cannot be drawn."
            )
            self._resolution_rings_check_box.setChecked(False)
        else:
            self._resolution_rings_canvas.setData(
                [self._img_center_x] * len(resolution_rings_in_pix),
                [self._img_center_y] * len(resolution_rings_in_pix),
                symbol="o",
                size=resolution_rings_in_pix,
                pen=self._resolution_rings_pen,
                brush=(255, 255, 255, 0),
                pxMode=False,
            )

            for index, item in enumerate(self._resolution_rings_textitems):
                item.setPos(
                    (self._img_center_x + resolution_rings_in_pix[index + 1] / 2.0),
                    self._img_center_y,
                )

    def _back_button_clicked(self):
        # Manages clicks on the 'back' button.
        if self._current_event > 0:
            self._current_event -= 1
        else:
            self._current_event = self._num_events - 1
        self._update_image_and_peaks()

    def _forward_button_clicked(self):
        # Manages clicks on the 'back' button.
        if self._current_event < self._num_events - 1:
            self._current_event += 1
        else:
            self._current_event = 0
        self._update_image_and_peaks()

    def _random_button_clicked(self):
        # Manages clicks on the 'random' button.
        self._current_event = randrange(self._num_events)
        self._update_image_and_peaks()

    def _update_image_and_peaks(self):
        # Updates the image and Bragg peaks shown by the viewer.
        if self._multi_event:
            filename, indx = self._events[self._current_event]
            data = self._input_files[filename][self._hdf5_data_path][indx]
        else:
            filename = self._events[self._current_event]
            indx = -1
            data = self._input_files[filename][self._hdf5_data_path][()]

        self._frame_data_img[
            self._visual_pixelmap_y, self._visual_pixelmap_x
        ] = data.ravel().astype(self._frame_data_img.dtype)

        self._image_view.setImage(
            self._frame_data_img.T,
            autoLevels=False,
            levels=self._levels_range,
            autoRange=False,
            autoHistogramRange=False,
        )
        self._update_peaks()
        self.statusBar().showMessage("Showing {0}, event {1}".format(filename, indx))

    def _update_peaks(self):
        # Updates the Bragg peaks shown by the viewer.
        peak_list_y_in_frame = []
        peak_list_x_in_frame = []
        if self._show_peaks_check_box.isChecked():
            filename, indx = self._events[self._current_event]
            num_peaks = self._input_files[filename][self._hdf5_peaks_path]["nPeaks"][
                indx
            ]
            for peak_fs, peak_ss in zip(
                self._input_files[filename][self._hdf5_peaks_path]["peakXPosRaw"][indx][
                    :num_peaks
                ],
                self._input_files[filename][self._hdf5_peaks_path]["peakYPosRaw"][indx][
                    :num_peaks
                ],
            ):
                peak_index_in_slab: int = int(round(peak_ss)) * self._data_shape[
                    1
                ] + int(round(peak_fs))
                y_in_frame: float = self._visual_pixelmap_y[peak_index_in_slab]
                x_in_frame: float = self._visual_pixelmap_x[peak_index_in_slab]
                peak_list_x_in_frame.append(y_in_frame)
                peak_list_y_in_frame.append(x_in_frame)
        self._peak_canvas.setData(
            x=peak_list_y_in_frame,
            y=peak_list_x_in_frame,
            symbol="o",
            brush=(255, 255, 255, 0),
            size=[5] * len(peak_list_x_in_frame),
            pen=self._ring_pen,
            pxMode=False,
        )

    def _mouse_moved(self, pos):
        data = self._image_view.image
        n_rows, n_cols = data.shape
        scene_pos = self._image_view.getImageItem().mapFromScene(pos)
        row, col = int(scene_pos.x()), int(scene_pos.y())
        if (0 <= row < n_rows) and (0 <= col < n_cols):
            value = data[row, col]
        else:
            value = numpy.nan
        self._values_widget.setText("Intensity = {:.4f}".format(value))


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument(
    "input",
    nargs=-1,
    type=click.Path(exists=True),
)
@click.option(
    "--geometry",
    "-g",
    "geometry_filename",
    nargs=1,
    type=click.Path(exists=True),
    required=True,
)
@click.option(
    "--hdf5-data-path",
    "-d",
    "hdf5_data_path",
    nargs=1,
    type=str,
    required=False,
)
@click.option(
    "--hdf5-peaks-path",
    "-p",
    "hdf5_peaks_path",
    nargs=1,
    type=str,
    required=False,
)
def main(input, geometry_filename, hdf5_data_path, hdf5_peaks_path):
    """ """
    app = QtWidgets.QApplication(sys.argv)
    win = FrameViewerGui(input, geometry_filename, hdf5_data_path, hdf5_peaks_path)
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
