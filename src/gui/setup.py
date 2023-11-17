import os
import sys
import shutil
import zipfile
import requests
import subprocess
import pkg_resources
from PyQt5 import uic
from time import sleep
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QPushButton, QProgressBar


class SetupWindow(QMainWindow):
    def __init__(self, destination_folder: str, project_name: str, selected_release: list, initialize_on_setup: bool):
        super(SetupWindow, self).__init__()

        self.ui_file = './src/gui/ui/setup.ui'
        self.destination_folder = destination_folder
        self.project_name = project_name.lower().replace(' ', '_')
        self.selected_release = selected_release
        self.initialize_on_setup = initialize_on_setup

        self.total_tasks = 5 if initialize_on_setup else 4
        self.task_done = -1

        # Load ui file
        uic.loadUi(self.ui_file, self)

        # Define widgets
        self.titleLabel = self.findChild(QLabel, "titleLabel")
        self.projectName = self.findChild(QLabel, "projectName")
        self.installLocation = self.findChild(QLabel, "installLocation")
        self.selectedVersion = self.findChild(QLabel, "selectedVersion")
        self.initializeStatus = self.findChild(QLabel, "initializeStatus")
        self.currentStatus = self.findChild(QLabel, "currentStatus")
        self.statusTitle = self.findChild(QLabel, "statusTitle")
        self.progressBar = self.findChild(QProgressBar, "progressBar")
        self.finishButton = self.findChild(QPushButton, "finishButton")
        self.openFolderButton = self.findChild(QPushButton, "openFolderButton")
        self.openInCodeButton = self.findChild(QPushButton, "openInCodeButton")
        self.startSetupButton = self.findChild(QPushButton, "startSetupButton")

        # Set values
        self.projectName.setText(self.project_name)
        self.installLocation.setText(self.destination_folder)
        self.selectedVersion.setText(self.selected_release['tag'])
        self.initializeStatus.setText(
            'True' if self.initialize_on_setup else 'False')

        # Hide Widgets
        self.finishButton.hide()
        self.openFolderButton.hide()
        self.openInCodeButton.hide()

        # Connections
        self.startSetupButton.clicked.connect(lambda: self.prepare_php_launcher())
        self.openFolderButton.clicked.connect(lambda: self.open_in_explorer())
        self.openInCodeButton.clicked.connect(lambda: self.open_in_vscode())
        self.finishButton.clicked.connect(lambda: exit())

        # Show ui
        self.show()

    def update_task(self, next_task_message: str):
        self.task_done += 1
        self.progressBar.setValue(round((self.task_done / self.total_tasks) * 100))
        self.currentStatus.setText(next_task_message)
        sleep(0.1)

    def download_and_extract_zip(self, zip_filename: str, folder: str):
        # Download the ZIP archive
        response = requests.get(self.selected_release['url'])
        response.raise_for_status()

        # Create a temporary file to store the ZIP archive
        with open(zip_filename, 'wb') as zip_file:
            zip_file.write(response.content)

        self.update_task('Extracting project files...')
        # Extract the ZIP archive to a temporary folder
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall(folder)

    def get_first_folder_name(self, folder: str):
        if folder_contents := os.listdir(folder):
            # Get the name of the first directory inside the temporary folder
            first_directory_name = next(
                item for item in folder_contents if os.path.isdir(os.path.join(folder, item)))
            return os.path.join(folder, first_directory_name)
        else:
            return null

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
            os.rmdir(folder)

    def open_in_vscode(self):
        os.chdir(os.path.join(self.destination_folder, self.project_name))
        command = 'code .'
        subprocess.call(command, shell=True)
        exit()

    def open_in_explorer(self):
        os.chdir(os.path.join(self.destination_folder, self.project_name))
        subprocess.call('explorer .', shell=True)
        exit()

    def project_initialize(self, target: str):
        os.chdir(target)
        subprocess.run(['php', 'launch', 'install', '-q'])

    def prepare_php_launcher(self):
        # Hide Setup Btn
        self.startSetupButton.hide()
        
        self.titleLabel.setText('Preparing PHP Launcher...')

        zip_filename = 'temp_repo.zip'
        temp_folder = 'temp_repo_extracted'

        self.update_task('Downloading project files...')
        try:
            # Task 1 & 2: Download and Extract Zip
            self.download_and_extract_zip(zip_filename, temp_folder)
            extracted_folder = self.get_first_folder_name(temp_folder)
            if (extracted_folder is None):
                return

            # Task 3: Move to Destination
            self.update_task('Moving project files...')
            self.move_to_destination_and_remove_unreq_files(extracted_folder)

            # Task 4: Clean Up
            self.update_task('Preparing project...')
            self.project_clean_up([zip_filename], [temp_folder])

            # Task 5: Setup
            if self.initialize_on_setup:
                self.update_task('Initializing project...')
                installed_at = f'{self.destination_folder}/{self.project_name}'
                self.project_initialize(installed_at)
            
            self.update_task('Completed.')

            # Show Buttons
            self.finishButton.show()
            self.openFolderButton.show()
            self.openInCodeButton.show()

            self.titleLabel.setText('PHP Launcher Project Ready!')

        except Exception as e:
            print("An error occurred:", e)
