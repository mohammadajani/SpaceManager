import os
import shutil
import sys
import time
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox,
    QSystemTrayIcon, QMenu, QAction, QWidget
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon

class FileMoverWorker(QThread):
    # Signal to notify the main app when a file has been moved
    file_moved = pyqtSignal(str)

    def __init__(self, downloads_folder, target_folder, days_threshold, interval=3600):
        super().__init__()
        self.downloads_folder = downloads_folder
        self.target_folder = target_folder
        self.days_threshold = days_threshold
        self.interval = interval
        self.running = True

    def run(self):
        while self.running:
            # Check for files older than threshold and move them
            self.move_old_files()
            time.sleep(self.interval)  # Check every 'interval' seconds

    def move_old_files(self):
        time_threshold = datetime.now() - timedelta(days=self.days_threshold)

        for filename in os.listdir(self.downloads_folder):
            file_path = os.path.join(self.downloads_folder, filename)
            if os.path.isfile(file_path):
                file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_mod_time < time_threshold:
                    shutil.move(file_path, self.target_folder)
                    self.file_moved.emit(filename)  # Notify the app that a file was moved

    def stop(self):
        self.running = False


class FileMoverApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automatic File Mover")
        self.setGeometry(300, 300, 400, 200)

        # Set up the user interface
        self.downloads_folder = ""
        self.target_folder = ""
        self.days_threshold = 10

        # UI Elements
        self.downloads_folder_label = QLabel("Downloads Folder:", self)
        self.downloads_folder_label.move(20, 20)
        self.downloads_folder_input = QLineEdit(self)
        self.downloads_folder_input.setGeometry(150, 20, 200, 25)
        self.downloads_folder_button = QPushButton("Browse", self)
        self.downloads_folder_button.setGeometry(360, 20, 80, 25)
        self.downloads_folder_button.clicked.connect(self.browse_downloads_folder)

        self.target_folder_label = QLabel("Target Folder:", self)
        self.target_folder_label.move(20, 60)
        self.target_folder_input = QLineEdit(self)
        self.target_folder_input.setGeometry(150, 60, 200, 25)
        self.target_folder_button = QPushButton("Browse", self)
        self.target_folder_button.setGeometry(360, 60, 80, 25)
        self.target_folder_button.clicked.connect(self.browse_target_folder)

        self.days_label = QLabel("Days Threshold:", self)
        self.days_label.move(20, 100)
        self.days_input = QLineEdit(self)
        self.days_input.setGeometry(150, 100, 50, 25)
        self.days_input.setText("10")

        self.start_button = QPushButton("Start Monitoring", self)
        self.start_button.setGeometry(150, 140, 120, 30)
        self.start_button.clicked.connect(self.start_monitoring)

        # Tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))  # Replace with an icon file path
        tray_menu = QMenu()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_app)
        tray_menu.addAction(exit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # Worker thread for background file moving
        self.worker = None

    def browse_downloads_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Downloads Folder")
        if folder:
            self.downloads_folder = folder
            self.downloads_folder_input.setText(folder)

    def browse_target_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Target Folder")
        if folder:
            self.target_folder = folder
            self.target_folder_input.setText(folder)

    def start_monitoring(self):
        self.downloads_folder = self.downloads_folder_input.text()
        self.target_folder = self.target_folder_input.text()
        self.days_threshold = int(self.days_input.text())

        if not self.downloads_folder or not self.target_folder:
            QMessageBox.warning(self, "Input Error", "Please select both folders.")
            return

        # Start the background worker thread
        self.worker = FileMoverWorker(self.downloads_folder, self.target_folder, self.days_threshold)
        self.worker.file_moved.connect(self.notify_file_moved)
        self.worker.start()
        self.tray_icon.show()
        self.hide()
        QMessageBox.information(self, "Monitoring Started", "The application is now monitoring the downloads folder in the background.")

    def notify_file_moved(self, filename):
        self.tray_icon.showMessage("File Moved", f"Moved: {filename}", QSystemTrayIcon.Information, 3000)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.showNormal()  # Show the app when the tray icon is clicked

    def exit_app(self):
        if self.worker:
            self.worker.stop()
        QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "File Mover",
            "Application minimized to tray. Right-click the tray icon to exit.",
            QSystemTrayIcon.Information,
            3000
        )


# Run the application
app = QApplication(sys.argv)
file_mover_app = FileMoverApp()
file_mover_app.show()
sys.exit(app.exec_())
