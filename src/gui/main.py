import os
import sys
import shutil
import zipfile
import requests
import subprocess
import pkg_resources
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget, QMainWindow, QLineEdit, QLabel, QCheckBox, QPushButton, QListWidget

class MainWindow(QMainWindow):
    def __init__(self, App):
        super(MainWindow, self).__init__()

        self.app = App
        self.releases = []
        self.initialize_on_setup = False
        self.list_unstable = False
        self.repo_name = 'php_launcher'
        self.repo_owner = 'hind-sagar-biswas'
        self.ui_file = './src/gui/ui/main-dark.ui'
        
        # Load ui file
        uic.loadUi(self.ui_file, self)

        # Define widgets
        self.installLocationInput = self.findChild(QLineEdit, "installLocationInput")
        self.selectLocationButton = self.findChild(QPushButton, "selectLocationButton")
        self.projectNameInput = self.findChild(QLineEdit, "projectNameInput")
        self.releasedVersionsList = self.findChild(QListWidget, "releasedVersionsList")
        self.prepareLauncherButton = self.findChild(QPushButton, "prepareLauncherButton")
        self.listUnstableCheckBox = self.findChild(QCheckBox, "listUnstableCheckBox")
        self.initOnLaunchCheckBox = self.findChild(QCheckBox, "initOnLaunchCheckBox")

        # Connections
        self.selectLocationButton.clicked.connect(lambda: self.select_location())
        self.prepareLauncherButton.clicked.connect(lambda: self.setup())
        self.initOnLaunchCheckBox.stateChanged.connect(lambda: self.toggle_init_on_setup())
        self.listUnstableCheckBox.stateChanged.connect(lambda: self.toggle_list_unstable())

        # Load Releases into the list
        self.load_releases()

        # Show ui
        self.show()

    def get_installation_location(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        return dialog.selectedFiles()[0] if dialog.exec_() else None

    def fetch_release_info(self):
        releases_url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases'
        response = requests.get(releases_url)
        releases = []

        if response.status_code == 200:
            release_info = response.json()
            for i in release_info:
                if not i.get('draft'):
                    if not i.get('prerelease'):
                                releases.append({
                            "tag": i.get('tag_name'),
                            "url": i.get('zipball_url'),
                            "pre": i.get('prerelease'),
                        })
                    elif self.list_unstable:
                                    releases.append({
                            "tag": i.get('tag_name'),
                            "url": i.get('zipball_url'),
                            "pre": i.get('prerelease'),
                        })

        releases.append({
            "tag": "main",
            "url": f'https://github.com/{self.repo_owner}/{self.repo_name}/archive/main.zip',
            "pre": True,
        })

        return releases

    def toggle_init_on_setup(self):
        self.initialize_on_setup = self.initOnLaunchCheckBox.isChecked()

    def toggle_list_unstable(self):
        self.list_unstable = self.listUnstableCheckBox.isChecked()
        self.load_releases()

    def select_location(self):
        location = self.get_installation_location()
        self.installLocationInput.setText(location)

    def load_releases(self):
        self.releasedVersionsList.clear()
        self.releases = self.fetch_release_info()
        for release in self.releases:
            self.releasedVersionsList.addItem(release['tag'])

    def setup(self):
        selected_index = self.releasedVersionsList.currentRow()
        selected_release = self.releases[selected_index if selected_index != -1 else 0]
        destination_folder = self.installLocationInput.text()
        new_project_name = self.projectNameInput.text()

        self.app.setup(destination_folder, new_project_name, selected_release, self.initialize_on_setup)
