import os
import sys
import shutil
import zipfile
import argparse
import requests
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(description="CLI for taking arguments")

    # Positional argument
    parser.add_argument("name", help="Project Name (compulsory)")

    # Optional arguments
    parser.add_argument("-v", "--version", help="Version (optional)")
    parser.add_argument("-l", "--location",
                        help="Location (optional)", default=os.getcwd())
    parser.add_argument("-q", action="store_true", help="Flag q (optional)")

    return parser.parse_args()


def main():
    args = parse_args()

    print("PHP Launchpad CLI v2.0.0")

    if install_location := args.location:
        new_project_name = args.name.replace(' ', '_').replace('-', '_')
        version = args.version or 'main'
        repo_owner = 'hind-sagar-biswas'
        repo_name = 'php_launcher'
        init_on_setup = args.q

        print('')
        print(f'|\tProject Name : {new_project_name}')
        print(f'|\tInstall DIR  : {install_location}')
        print(f'|\tSelected Ver : {version}')
        print(f'|\tInit on Setup: {init_on_setup}')

        abort = input('\nDo you want to proceed? [Y/n]\n>>')
        if abort in ['n', 'N']: sys.exit()

        fetch_and_rename_git_repo(repo_owner, repo_name, install_location, new_project_name, version, init_on_setup)


def fetch_release_info(repo_owner: str, repo_name: str):
    releases_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/releases'
    response = requests.get(releases_url)
    releases = {
        "main" : {
            "tag": "main",
            "url": f'https://github.com/{repo_owner}/{repo_name}/archive/main.zip',
            "pre": True,
        }
    }

    if response.status_code == 200:
        release_info = response.json()
        for i in release_info:
            if i.get('draft'): continue
            releases[i.get('tag_name')] = {
                "tag": i.get('tag_name'),
                "url": i.get('zipball_url'),
                "pre": i.get('prerelease'),
            }
    return releases


def select_release(releases: list, select: str = 'main'):
    if select not in releases: 
        print(f'\033[1;31;40mRequested {select} version not found!\033[1;0;40m')
        print('Defaulting to `\033[1;33;40mmain\033[1;0;40m` branch.')
        select = 'main'

        abort = input('Do you want to proceed? [Y/n]\n>>')
        if abort in ['n', 'N']: sys.exit()
    return releases[select]['url']

def fetch_and_rename_git_repo(
    repo_owner: str,
    repo_name: str,
    destination_folder: str,
    new_project_name: str,
    version: str,
    init_on_setup: bool
):
    zip_filename = 'temp_repo.zip'
    temp_folder = 'temp_repo_extracted'

    try:
        releases = fetch_release_info(repo_owner, repo_name)
        release_url = select_release(
            releases, f'v{version}' if version != 'main' else 'main'
        )

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
            first_directory_name = next(item for item in temp_folder_contents if os.path.isdir(
                os.path.join(temp_folder, item)))
            extracted_folder = os.path.join(temp_folder, first_directory_name)
        else:
            print("\033[1;31;40mNo directories found inside the temporary folder.\033[1;0;40m")
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

        installed_at = f'{destination_folder}\{new_project_name}'
        print("PHP Launcher successfully prepared @ \033[1;33;40m", installed_at, "\033[1;0;40m")

        if init_on_setup:
            os.chdir(installed_at)
            subprocess.run(['php', 'launch'])

    except Exception as e:
        print("An error occurred:", e)


if __name__ == "__main__":
    running = True
    while running:
        main()
        running = False
