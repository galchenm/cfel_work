# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dataCollectionDialog.ui'
#
# Created: Tue Oct 24 14:21:16 2017
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_dialogDataCollection(object):
    def setupUi(self, dialogDataCollection):
        dialogDataCollection.setObjectName(_fromUtf8("dialogDataCollection"))
        dialogDataCollection.setWindowModality(QtCore.Qt.ApplicationModal)
        dialogDataCollection.resize(378, 531)
        self.gridLayout = QtGui.QGridLayout(dialogDataCollection)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_24 = QtGui.QLabel(dialogDataCollection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_24.sizePolicy().hasHeightForWidth())
        self.label_24.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_24.setFont(font)
        self.label_24.setObjectName(_fromUtf8("label_24"))
        self.gridLayout.addWidget(self.label_24, 0, 1, 1, 1)
        self.label_43 = QtGui.QLabel(dialogDataCollection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_43.sizePolicy().hasHeightForWidth())
        self.label_43.setSizePolicy(sizePolicy)
        self.label_43.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_43.setObjectName(_fromUtf8("label_43"))
        self.gridLayout.addWidget(self.label_43, 2, 2, 1, 1)
        self.labelDataCollectionSpeed = QtGui.QLabel(dialogDataCollection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelDataCollectionSpeed.sizePolicy().hasHeightForWidth())
        self.labelDataCollectionSpeed.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.labelDataCollectionSpeed.setFont(font)
        self.labelDataCollectionSpeed.setFrameShape(QtGui.QFrame.Box)
        self.labelDataCollectionSpeed.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.labelDataCollectionSpeed.setMargin(2)
        self.labelDataCollectionSpeed.setObjectName(_fromUtf8("labelDataCollectionSpeed"))
        self.gridLayout.addWidget(self.labelDataCollectionSpeed, 1, 2, 1, 1)
        self.labelDegreesTotal = QtGui.QLabel(dialogDataCollection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelDegreesTotal.sizePolicy().hasHeightForWidth())
        self.labelDegreesTotal.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.labelDegreesTotal.setFont(font)
        self.labelDegreesTotal.setFrameShape(QtGui.QFrame.Box)
        self.labelDegreesTotal.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.labelDegreesTotal.setMargin(2)
        self.labelDegreesTotal.setObjectName(_fromUtf8("labelDegreesTotal"))
        self.gridLayout.addWidget(self.labelDegreesTotal, 3, 1, 1, 1)
        self.verticalLayoutDataCollectionStatus = QtGui.QVBoxLayout()
        self.verticalLayoutDataCollectionStatus.setObjectName(_fromUtf8("verticalLayoutDataCollectionStatus"))
        self.gridLayout.addLayout(self.verticalLayoutDataCollectionStatus, 4, 1, 1, 2)
        self.labelDataCollectionProgress = QtGui.QLabel(dialogDataCollection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelDataCollectionProgress.sizePolicy().hasHeightForWidth())
        self.labelDataCollectionProgress.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.labelDataCollectionProgress.setFont(font)
        self.labelDataCollectionProgress.setTextFormat(QtCore.Qt.PlainText)
        self.labelDataCollectionProgress.setAlignment(QtCore.Qt.AlignCenter)
        self.labelDataCollectionProgress.setMargin(3)
        self.labelDataCollectionProgress.setObjectName(_fromUtf8("labelDataCollectionProgress"))
        self.gridLayout.addWidget(self.labelDataCollectionProgress, 6, 1, 1, 2)
        self.label_41 = QtGui.QLabel(dialogDataCollection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_41.sizePolicy().hasHeightForWidth())
        self.label_41.setSizePolicy(sizePolicy)
        self.label_41.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_41.setObjectName(_fromUtf8("label_41"))
        self.gridLayout.addWidget(self.label_41, 2, 1, 1, 1)
        self.label_42 = QtGui.QLabel(dialogDataCollection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_42.sizePolicy().hasHeightForWidth())
        self.label_42.setSizePolicy(sizePolicy)
        self.label_42.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_42.setObjectName(_fromUtf8("label_42"))
        self.gridLayout.addWidget(self.label_42, 0, 2, 1, 1)
        self.pushButtonStopDataCollection = QtGui.QPushButton(dialogDataCollection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButtonStopDataCollection.sizePolicy().hasHeightForWidth())
        self.pushButtonStopDataCollection.setSizePolicy(sizePolicy)
        self.pushButtonStopDataCollection.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.pushButtonStopDataCollection.setIconSize(QtCore.QSize(16, 16))
        self.pushButtonStopDataCollection.setObjectName(_fromUtf8("pushButtonStopDataCollection"))
        self.gridLayout.addWidget(self.pushButtonStopDataCollection, 8, 1, 1, 2)
        self.labelCollectionTime = QtGui.QLabel(dialogDataCollection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelCollectionTime.sizePolicy().hasHeightForWidth())
        self.labelCollectionTime.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.labelCollectionTime.setFont(font)
        self.labelCollectionTime.setFrameShape(QtGui.QFrame.Box)
        self.labelCollectionTime.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.labelCollectionTime.setMargin(2)
        self.labelCollectionTime.setObjectName(_fromUtf8("labelCollectionTime"))
        self.gridLayout.addWidget(self.labelCollectionTime, 3, 2, 1, 1)
        self.labelDataCollectionTimeRemaining = QtGui.QLabel(dialogDataCollection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelDataCollectionTimeRemaining.sizePolicy().hasHeightForWidth())
        self.labelDataCollectionTimeRemaining.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.labelDataCollectionTimeRemaining.setFont(font)
        self.labelDataCollectionTimeRemaining.setFrameShape(QtGui.QFrame.Box)
        self.labelDataCollectionTimeRemaining.setMargin(2)
        self.labelDataCollectionTimeRemaining.setObjectName(_fromUtf8("labelDataCollectionTimeRemaining"))
        self.gridLayout.addWidget(self.labelDataCollectionTimeRemaining, 1, 1, 1, 1)
        self.progressBarDataCollection = QtGui.QProgressBar(dialogDataCollection)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.progressBarDataCollection.setFont(font)
        self.progressBarDataCollection.setProperty("value", 0)
        self.progressBarDataCollection.setObjectName(_fromUtf8("progressBarDataCollection"))
        self.gridLayout.addWidget(self.progressBarDataCollection, 7, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 1, 1, 2)

        self.retranslateUi(dialogDataCollection)
        QtCore.QMetaObject.connectSlotsByName(dialogDataCollection)

    def retranslateUi(self, dialogDataCollection):
        dialogDataCollection.setWindowTitle(_translate("dialogDataCollection", "DataCollection", None))
        self.label_24.setText(_translate("dialogDataCollection", "Time remaining", None))
        self.label_43.setText(_translate("dialogDataCollection", "Collection time", None))
        self.labelDataCollectionSpeed.setText(_translate("dialogDataCollection", "xx", None))
        self.labelDegreesTotal.setText(_translate("dialogDataCollection", "xxx.xxxD", None))
        self.labelDataCollectionProgress.setText(_translate("dialogDataCollection", "Data collection idle", None))
        self.label_41.setText(_translate("dialogDataCollection", "Degrees total", None))
        self.label_42.setText(_translate("dialogDataCollection", "Speed", None))
        self.pushButtonStopDataCollection.setText(_translate("dialogDataCollection", "Stop\n"
"data collection", None))
        self.labelCollectionTime.setText(_translate("dialogDataCollection", "00:00:00", None))
        self.labelDataCollectionTimeRemaining.setText(_translate("dialogDataCollection", "00:00:00", None))

