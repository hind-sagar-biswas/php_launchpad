import os
import sys
import shutil
import zipfile
import requests
import subprocess
from PyQt5.QtWidgets import QApplication, QFileDialog

# Function to open a file dialog and get the installation location
def get_installation_location():
    app = QApplication(sys.argv)
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.Directory)

    return dialog.selectedFiles()[0] if dialog.exec_() else None

# Function to fetch a Git repository from GitHub and save it with a different name
def fetch_and_rename_git_repo(repo_owner, repo_name, destination_folder, new_project_name):
    zip_filename = 'temp_repo.zip'
    temp_folder = 'temp_repo_extracted'
    releases_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest'

    try:
        # Check for the latest release
        response = requests.get(releases_url)
        if response.status_code == 200:
            release_info = response.json()
            release_tag_name = release_info.get('tag_name')
            print(f"Latest release found: {release_tag_name}")
            release_url = release_info.get('zipball_url')
        else:
            print("No Stable release found! defaulting to main branch")
            release_tag_name = 'main'  # Default to 'main' if no release is found
            release_url = f'https://github.com/{repo_owner}/{repo_name}/archive/main.zip'

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
        print("PHP Launcher successfully downloaded to:", installed_at)
        initiate = input("Initiate Now? [y/N]")

        if initiate.lower() in ('y', 'yes'):
            os.chdir(installed_at)
            subprocess.run(['php', 'launch'])

    except Exception as e:
        print("An error occurred:", e)

running = True
while running:
    print("PHP Launcher Installation Script")

    # Prompt for the GitHub repository owner and name
    repo_owner = 'hind-sagar-biswas'
    repo_name = 'php_launcher'

    # Prompt for the desired project name
    new_project_name = input('Enter the desired project name: ').replace(' ', '_').replace('-', '_')

    if install_location := get_installation_location():
        fetch_and_rename_git_repo(repo_owner, repo_name, install_location, new_project_name)
    running = False