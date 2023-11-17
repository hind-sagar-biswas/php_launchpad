import sys
from main import MainWindow
from setup import SetupWindow
from PyQt5.QtWidgets import QApplication

class App():
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.mainWindow = MainWindow(self)
    
    def run(self):
        sys.exit(self.app.exec_())

    def setup(self, destination_folder: str, project_name: str, selected_release: list, initialize_on_setup: bool):
        self.mainWindow.hide()

        self.setupWindow = SetupWindow(destination_folder, project_name, selected_release, initialize_on_setup)
        self.setupWindow.show()
        self.setupWindow.prepare_php_launcher()

if __name__ == "__main__":
    app = App()
    app.run()