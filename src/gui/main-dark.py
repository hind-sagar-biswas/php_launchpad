import os
import sys
import shutil
import zipfile
import requests
import subprocess
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def __init__(self):
        super().__init__()

        self.repo_name = 'php_launcher'
        self.repo_owner = 'hind-sagar-biswas'

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(461, 516)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./src/favicon.ico"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setToolTipDuration(1)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet("background-color: #0d1117; color: #bec6cd;")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.installLocationInput = QtWidgets.QLineEdit(self.centralwidget)
        self.installLocationInput.setGeometry(QtCore.QRect(10, 80, 281, 31))
        self.installLocationInput.setStyleSheet(
            "border: 1px solid grey; border-radius: 5px;")
        self.installLocationInput.setObjectName("installLocationInput")
        self.selectLocationButton = QtWidgets.QPushButton(
            self.centralwidget, clicked=lambda: self.select_location())
        self.selectLocationButton.setGeometry(QtCore.QRect(300, 80, 151, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.selectLocationButton.setFont(font)
        self.selectLocationButton.setStyleSheet(
            "background-color: #30363d; color: #eaf3ff; border: 1px solid grey; border-radius: 5px;")
        self.selectLocationButton.setObjectName("selectLocationButton")
        self.projectNameInput = QtWidgets.QLineEdit(self.centralwidget)
        self.projectNameInput.setGeometry(QtCore.QRect(10, 10, 441, 61))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.projectNameInput.setFont(font)
        self.projectNameInput.setStyleSheet(
            "padding: 10px; border: 1px solid grey; border-radius: 5px;")
        self.projectNameInput.setObjectName("projectNameInput")
        self.releasedVersionsList = QtWidgets.QListWidget(self.centralwidget)
        self.releasedVersionsList.setGeometry(QtCore.QRect(10, 160, 441, 221))
        self.releasedVersionsList.setStyleSheet(
            "border: 1px solid grey; border-radius: 5px;")
        self.releasedVersionsList.setObjectName("releasedVersionsList")
        self.selectVersionButton = QtWidgets.QPushButton(self.centralwidget)
        self.selectVersionButton.setGeometry(QtCore.QRect(310, 390, 141, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.selectVersionButton.setFont(font)
        self.selectVersionButton.setStyleSheet(
            "background-color: #30363d; color: #eaf3ff; border: 1px solid grey; border-radius: 5px;")
        self.selectVersionButton.setObjectName("selectVersionButton")
        self.prepareLauncherButton = QtWidgets.QPushButton(self.centralwidget)
        self.prepareLauncherButton.setGeometry(QtCore.QRect(310, 430, 141, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.prepareLauncherButton.setFont(font)
        self.prepareLauncherButton.setStyleSheet(
            "background-color: #7a37a3; color: #eaf3ff; border-radius: 5px;")
        self.prepareLauncherButton.setObjectName("prepareLauncherButton")
        self.initOnLaunchCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.initOnLaunchCheckBox.setGeometry(QtCore.QRect(10, 390, 251, 20))
        self.initOnLaunchCheckBox.setStyleSheet("color: #89929c;")
        self.initOnLaunchCheckBox.setObjectName("initOnLaunchCheckBox")
        self.selectVersionLabel = QtWidgets.QLabel(self.centralwidget)
        self.selectVersionLabel.setGeometry(QtCore.QRect(10, 120, 441, 31))
        self.selectVersionLabel.setStyleSheet("color: #89929c;")
        self.selectVersionLabel.setObjectName("selectVersionLabel")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 461, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.load_releases()

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate(
            "MainWindow", "PHP Launchpad v1.3.0"))
        self.installLocationInput.setText(_translate("MainWindow", "C:/"))
        self.selectLocationButton.setText(
            _translate("MainWindow", "Browse Location"))
        self.projectNameInput.setPlaceholderText(
            _translate("MainWindow", "Name of the project"))
        self.selectVersionButton.setText(
            _translate("MainWindow", "Select Version"))
        self.prepareLauncherButton.setText(
            _translate("MainWindow", "Setup Launcher"))
        self.initOnLaunchCheckBox.setText(_translate(
            "MainWindow", "Initialize project quitly on installation?"))
        self.selectVersionLabel.setText(_translate(
            "MainWindow", "Select the version you want to setup from below"))

    # Method to open a file dialog and get the installation location
    def get_installation_location(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        return dialog.selectedFiles()[0] if dialog.exec_() else None

    def fetch_release_info(self):
        releases_url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases'
        response = requests.get(releases_url)
        releases = []

        if response.status_code == 200:
            release_info = response.json()
            releases.extend(
                {
                    "tag": i.get('tag_name'),
                    "url": i.get('zipball_url'),
                    "pre": i.get('prerelease'),
                }
                for i in release_info
                if not i.get('draft')
            )
        releases.append({
            "tag": "main",
            "url": f'https://github.com/{self.repo_owner}/{self.repo_name}/archive/main.zip',
            "pre": True,
        })

        return releases

    def select_location(self):
        location = self.get_installation_location()
        self.installLocationInput.setText(location)

    def load_releases(self):
        releases = self.fetch_release_info()
        for release in releases:
            self.releasedVersionsList.addItem(release['tag'])


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
