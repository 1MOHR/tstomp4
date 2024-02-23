import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTextEdit, QCheckBox, QLabel
)
from PyQt6.QtCore import QThread, pyqtSignal

class ConvertThread(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, file_paths, output_path):
        super().__init__()
        self.file_paths = file_paths
        self.output_path = output_path

    def run(self):
        for file_path in self.file_paths:
            if not file_path.endswith('.ts'):
                self.update_signal.emit(f"Skipping unsupported file: {file_path}")
                continue
            
            output_folder = self.output_path or os.path.dirname(file_path)
            mp4_file_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(file_path))[0]}.mp4")

            command = ["ffmpeg", "-i", file_path, "-c:v", "copy", "-c:a", "aac", mp4_file_path]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.update_signal.emit(output.strip())
            process.stdout.close()
            process.wait()
        self.update_signal.emit('Conversion completed.')

class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('TS to MP4 Converter')
        self.resize(500, 400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel('Select TS files to convert to MP4:')
        layout.addWidget(self.label)

        self.file_paths = []

        self.select_button = QPushButton('Select Files')
        self.select_button.clicked.connect(self.select_files)
        layout.addWidget(self.select_button)

        self.convert_button = QPushButton('Convert')
        self.convert_button.clicked.connect(self.convert_files)
        self.convert_button.setEnabled(False)
        layout.addWidget(self.convert_button)

        self.check_box = QCheckBox('Custom output destination')
        self.check_box.toggled.connect(self.select_output_folder)
        layout.addWidget(self.check_box)

        self.output_path = None

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def select_files(self):
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
