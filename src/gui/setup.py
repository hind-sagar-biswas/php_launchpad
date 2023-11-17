import os
import sys
import shutil
import zipfile
import requests
import subprocess
import pkg_resources
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget, QMainWindow, QLineEdit, QLabel, QCheckBox, QPushButton, QListWidget, QMenuBar, QStatusBar


class SetupWindow(QMainWindow):
    def __init__(self, destination_folder: str, project_name: str, selected_release: list, initialize_on_setup: bool):
        super(SetupWindow, self).__init__()

        self.ui_file = './src/gui/ui/setup.ui'
        self.destination_folder = destination_folder
        self.project_name = project_name.lower().replace(' ', '_')
        self.selected_release = selected_release
        self.initialize_on_setup = initialize_on_setup

        # Load ui file
        uic.loadUi(self.ui_file, self)
        
        # Show ui
        self.show()

    def download_and_extract_zip(self, zip_filename: str, folder: str):
        # Download the ZIP archive
        response = requests.get(self.selected_release['url'])
        response.raise_for_status()

        # Create a temporary file to store the ZIP archive
        with open(zip_filename, 'wb') as zip_file:
            zip_file.write(response.content)

        # Extract the ZIP archive to a temporary folder
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall(folder)

    def get_first_folder_name(self, folder: str):
        if folder_contents := os.listdir(folder):
            # Get the name of the first directory inside the temporary folder
            first_directory_name = next(item for item in folder_contents if os.path.isdir(os.path.join(folder, item)))
            return os.path.join(folder, first_directory_name)
        else: return null

    def move_to_destination_and_remove_unreq_files(self, target):
        new_folder = os.path.join(self.destination_folder, self.project_name)
        shutil.move(target, new_folder)

        # Remove the .github folder from the downloaded repository
        github_folder = os.path.join(new_folder, '.github')
        if os.path.exists(github_folder):
            shutil.rmtree(github_folder)

    def project_clean_up(self, targetFiles=None, targetFolders=None):
        if targetFiles is None:
            targetFiles = []
        if targetFolders is None:
            targetFolders = []
        for file in targetFiles:
            os.remove(file)
        for folder in targetFolders:
            os.remove(folder)

    def project_initialize(self, target: str):
        os.chdir(installed_at)
        subprocess.run(['php', 'launch', 'install', '-q'])

    def prepare_php_launcher(self):
        zip_filename = 'temp_repo.zip'
        temp_folder = 'temp_repo_extracted'

        try:
            self.download_and_extract_zip(zip_filename, temp_folder)
            extracted_folder = self.get_first_folder_name(temp_folder)
            if (extracted_folder is null): return

            self.move_to_destination_and_remove_unreq_files(extracted_folder)
            self.project_clean_up([zip_filename], [temp_folder])

            if self.initialize_on_setup:
                installed_at = f'{self.destination_folder}/{self.project_name}'
                self.project_initialize(installed_at)

        except Exception as e:
            print("An error occurred:", e)
