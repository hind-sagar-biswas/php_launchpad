import os
import sys
import shutil
import zipfile
import requests
import subprocess
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget, QMainWindow, QLineEdit, QLabel, QCheckBox, QPushButton, QListWidget, QMenuBar, QStatusBar


class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        self.ui_file = './src/gui/ui/main-dark.ui'
        self.repo_name = 'php_launcher'
        self.repo_owner = 'hind-sagar-biswas'
        self.releases = []
        self.initialize_on_setup = False

        # Load ui file
        uic.loadUi(self.ui_file, self)

        # Define widgets
        self.installLocationInput = self.findChild(QLineEdit, "installLocationInput")
        self.selectLocationButton = self.findChild(QPushButton, "selectLocationButton")
        self.projectNameInput = self.findChild(QLineEdit, "projectNameInput")
        self.releasedVersionsList = self.findChild(QListWidget, "releasedVersionsList")
        self.prepareLauncherButton = self.findChild(QPushButton, "prepareLauncherButton")
        self.initOnLaunchCheckBox = self.findChild(QCheckBox, "initOnLaunchCheckBox")

        # Connections
        self.selectLocationButton.clicked.connect(lambda: self.select_location())
        self.prepareLauncherButton.clicked.connect(lambda: self.prepare_php_launcher())
        self.initOnLaunchCheckBox.stateChanged.connect(lambda: self.toggle_init_on_setup())
        
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

    def toggle_init_on_setup(self):
        self.initialize_on_setup = (self.initOnLaunchCheckBox.isChecked)

    def select_location(self):
        location = self.get_installation_location()
        self.installLocationInput.setText(location)

    def load_releases(self):
        self.releases = self.fetch_release_info()
        for release in self.releases:
            self.releasedVersionsList.addItem(release['tag'])

    def prepare_php_launcher(self):
        selected_index = self.releasedVersionsList.currentRow()
        selected_release = self.releases[selected_index if selected_index != -1 else 0]

        destination_folder = self.installLocationInput.text()
        new_project_name = self.projectNameInput.text().lower().replace(' ', '_')
        zip_filename = 'temp_repo.zip'
        temp_folder = 'temp_repo_extracted'

        try:
            release_url = selected_release['url']

            # Download the ZIP archive
            response = requests.get(release_url)
            response.raise_for_status()

            # Create a temporary file to store the ZIP archive
            with open(zip_filename, 'wb') as zip_file:
                zip_file.write(response.content)

            # Extract the ZIP archive to a temporary folder
            with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                zip_ref.extractall(temp_folder)

            if temp_folder_contents := os.listdir(temp_folder):
                # Get the name of the first directory inside the temporary folder
                first_directory_name = next(item for item in temp_folder_contents if os.path.isdir(os.path.join(temp_folder, item)))
                extracted_folder = os.path.join(temp_folder, first_directory_name)
            else:
                print("No directories found inside the temporary folder.")
                return

            # Move the extracted folder to the destination folder and use the specified project name
            new_folder = os.path.join(destination_folder, new_project_name)
            shutil.move(extracted_folder, new_folder)

            # Remove the .github folder from the downloaded repository
            github_folder = os.path.join(new_folder, '.github')
            if os.path.exists(github_folder):
                shutil.rmtree(github_folder)

            # Clean up the temporary ZIP file and folder
            os.remove(zip_filename)
            os.rmdir(temp_folder)

            installed_at = f'{destination_folder}/{new_project_name}'

            if self.initialize_on_setup:
                os.chdir(installed_at)
                subprocess.run(['php', 'launch', 'install', '-q'])

        except Exception as e:
            print("An error occurred:", e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    UIWindow = UI()
    sys.exit(app.exec_())