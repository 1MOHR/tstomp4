import sys
import os
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTextEdit, QCheckBox, QLabel
)

# Thread class for converting TS files to MP4
class ConvertThread(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, file_paths, output_path):
        super().__init__()
        self.file_paths = file_paths
        self.output_path = output_path

    def run(self):
        for file_path in self.file_paths:
            try:
                self.convert_file(file_path)
            except Exception as e:
                self.update_signal.emit(f"Error converting {file_path}: {e}")
        self.update_signal.emit('Conversion completed.')

    def convert_file(self, file_path):
        if not file_path.endswith('.ts'):
            self.update_signal.emit(f"Skipping unsupported file: {file_path}")
            return

        output_folder = self.output_path or os.path.dirname(file_path)
        mp4_file_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(file_path))[0]}.mp4")

        self.update_signal.emit(f"Converting {file_path} to {mp4_file_path}")
        command = ["ffmpeg", "-i", file_path, "-c:v", "copy", "-c:a", "aac", mp4_file_path]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        self.process_output(process)
        self.update_signal.emit(f"Conversion of {file_path} completed.")

    def process_output(self, process):
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.update_signal.emit(output.strip())
        process.stdout.close()
        process.wait()

# Main application class
class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('TS to MP4 Converter')
        self.resize(500, 400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Label for file selection
        self.label = QLabel('Select TS files to convert to MP4:')
        layout.addWidget(self.label)

        self.file_paths = []

        # Button to select files
        self.select_button = QPushButton('Select Files')
        self.select_button.clicked.connect(self.select_files)
        layout.addWidget(self.select_button)

        # Button to start conversion
        self.convert_button = QPushButton('Convert')
        self.convert_button.clicked.connect(self.convert_files)
        self.convert_button.setEnabled(False)
        layout.addWidget(self.convert_button)

        # Checkbox for custom output destination
        self.check_box = QCheckBox('Custom output destination')
        self.check_box.toggled.connect(self.select_output_folder)
        layout.addWidget(self.check_box)

        self.output_path = None

        # TextEdit widget to display log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def select_files(self):
        # Open file dialog to select TS files
        files, _ = QFileDialog.getOpenFileNames(self, 'Select Files', '', 'TS files (*.ts)')
        if files:
            self.file_paths = files
            self.convert_button.setEnabled(True)
            self.log_output.append('Files selected for conversion:')
            for file in files:
                self.log_output.append(file)

    def convert_files(self):
        self.convert_button.setEnabled(False)
        self.convert_thread = ConvertThread(self.file_paths, self.output_path)
        self.convert_thread.update_signal.connect(self.update_output)
        self.convert_thread.start()

    def update_output(self, text):
        self.log_output.append(text)

    def select_output_folder(self, checked):
        if checked:
            # Open folder dialog to select custom output folder
            self.output_path = QFileDialog.getExistingDirectory(self, 'Select Output Folder')
            if self.output_path:
                self.log_output.append(f'Custom output destination selected: {self.output_path}')
        else:
            self.output_path = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = AppDemo()
    demo.show()
    sys.exit(app.exec())
