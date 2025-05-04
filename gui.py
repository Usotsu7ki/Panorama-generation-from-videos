import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QSpinBox, QProgressBar, QMessageBox,
                            QSizePolicy, QGroupBox, QLineEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
import pano_generation
import get_key_frames
import subprocess

# Thread for processing video and extracting key frames
class VideoProcessor(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, video_path, stride):
        super().__init__()
        self.video_path = video_path
        self.stride = stride

    def run(self):
        try:
            # Extract key frames from video with specified stride
            get_key_frames.main(self.video_path, stride=self.stride)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

# Thread for generating panorama from key frames
class PanoramaGenerator(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, panorama_name):
        super().__init__()
        self.panorama_name = panorama_name

    def run(self):
        try:
            # Generate panorama with specified name
            pano_generation.main(self.panorama_name)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

# Main application window for panorama generation
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Panorama Generator")
        self.setMinimumSize(1000, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Configure main layout
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Video selection section
        video_group = QGroupBox("Video Selection")
        video_layout = QHBoxLayout()
        video_layout.setSpacing(10)
        
        self.video_label = QLabel("No video selected")
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.select_video_btn = QPushButton("Select Video")
        self.select_video_btn.setMinimumWidth(120)
        video_layout.addWidget(self.video_label)
        video_layout.addWidget(self.select_video_btn)
        video_group.setLayout(video_layout)
        layout.addWidget(video_group)
        
        # Parameters section
        params_group = QGroupBox("Parameters")
        params_layout = QHBoxLayout()
        params_layout.setSpacing(20)
        
        # Stride parameter
        stride_layout = QHBoxLayout()
        stride_label = QLabel("Stride:")
        self.stride_spin = QSpinBox()
        self.stride_spin.setRange(1, 100)
        self.stride_spin.setValue(10)
        self.stride_spin.setMinimumWidth(80)
        stride_layout.addWidget(stride_label)
        stride_layout.addWidget(self.stride_spin)
        stride_layout.addStretch()
        params_layout.addLayout(stride_layout)
        
        # Panorama name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Panorama Name:")
        self.panorama_name_edit = QLineEdit()
        self.panorama_name_edit.setPlaceholderText("panorama")
        self.panorama_name_edit.setMinimumWidth(200)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.panorama_name_edit)
        name_layout.addStretch()
        params_layout.addLayout(name_layout)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(25)
        layout.addWidget(self.progress_bar)
        
        # Action buttons section
        buttons_group = QGroupBox("Actions")
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        # Get Key Frames button
        self.get_keyframes_btn = QPushButton("Get Key Frames")
        self.get_keyframes_btn.setMinimumWidth(150)
        self.get_keyframes_btn.setMinimumHeight(40)
        buttons_layout.addWidget(self.get_keyframes_btn)
        
        # Browse Key Frames button
        self.browse_keyframes_btn = QPushButton("Open Key Frames Folder")
        self.browse_keyframes_btn.setMinimumWidth(150)
        self.browse_keyframes_btn.setMinimumHeight(40)
        self.browse_keyframes_btn.setEnabled(False)
        buttons_layout.addWidget(self.browse_keyframes_btn)
        
        # Generate Panorama button
        self.generate_btn = QPushButton("Generate Panorama")
        self.generate_btn.setMinimumWidth(150)
        self.generate_btn.setMinimumHeight(40)
        self.generate_btn.setEnabled(False)
        buttons_layout.addWidget(self.generate_btn)
        
        # Reset button
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setMinimumWidth(100)
        self.reset_btn.setMinimumHeight(40)
        buttons_layout.addWidget(self.reset_btn)
        
        buttons_group.setLayout(buttons_layout)
        layout.addWidget(buttons_group)
        
        # Preview area
        preview_group = QGroupBox("Panorama Preview")
        preview_layout = QVBoxLayout()
        preview_layout.setSpacing(10)
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview_label.setMinimumHeight(400)
        self.preview_label.setStyleSheet("QLabel { background-color: #f0f0f0; border: 1px solid #cccccc; }")
        preview_layout.addWidget(self.preview_label)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        main_widget.setLayout(layout)
        
        # Connect signals to slots
        self.select_video_btn.clicked.connect(self.select_video)
        self.get_keyframes_btn.clicked.connect(self.start_keyframe_extraction)
        self.browse_keyframes_btn.clicked.connect(self.open_keyframes_folder)
        self.generate_btn.clicked.connect(self.start_panorama_generation)
        self.reset_btn.clicked.connect(self.reset_ui)
        
        # Initialize variables
        self.video_path = None
        self.processor = None
        self.panorama_generator = None

    # Open file dialog to select video file
    def select_video(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov);;All Files (*)"
        )
        if file_name:
            self.video_path = file_name
            self.video_label.setText(os.path.basename(file_name))
            self.get_keyframes_btn.setEnabled(True)

    # Start the key frame extraction process
    def start_keyframe_extraction(self):
        if not self.video_path:
            QMessageBox.warning(self, "Warning", "Please select a video file first")
            return
        
        # Disable buttons during processing
        self.get_keyframes_btn.setEnabled(False)
        self.select_video_btn.setEnabled(False)
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Create and start processing thread
        self.processor = VideoProcessor(
            self.video_path,
            self.stride_spin.value()
        )
        self.processor.finished.connect(self.keyframe_extraction_finished)
        self.processor.error.connect(self.processing_error)
        self.processor.start()

    # Open the key_frames folder in system file explorer
    def open_keyframes_folder(self):
        key_frames_path = os.path.abspath('key_frames')
        if os.path.exists(key_frames_path):
            if sys.platform == 'win32':
                os.startfile(key_frames_path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', key_frames_path])
            else:  # linux
                subprocess.run(['xdg-open', key_frames_path])
        else:
            QMessageBox.warning(self, "Warning", "Key frames folder does not exist!")

    # Handle completion of key frame extraction
    def keyframe_extraction_finished(self):
        self.progress_bar.setValue(100)
        self.get_keyframes_btn.setEnabled(True)
        self.select_video_btn.setEnabled(True)
        self.browse_keyframes_btn.setEnabled(True)
        self.generate_btn.setEnabled(True)
        
        QMessageBox.information(self, "Complete", "Key frame extraction completed!")

    # Start the panorama generation process
    def start_panorama_generation(self):
        # Disable buttons during processing
        self.generate_btn.setEnabled(False)
        self.browse_keyframes_btn.setEnabled(False)
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Get panorama name
        panorama_name = self.panorama_name_edit.text().strip()
        if not panorama_name:
            panorama_name = "panorama"
        
        # Create and start panorama generation thread
        self.panorama_generator = PanoramaGenerator(panorama_name)
        self.panorama_generator.finished.connect(self.panorama_generation_finished)
        self.panorama_generator.error.connect(self.processing_error)
        self.panorama_generator.start()

    # Handle completion of panorama generation
    def panorama_generation_finished(self):
        self.progress_bar.setValue(100)
        self.generate_btn.setEnabled(True)
        self.browse_keyframes_btn.setEnabled(True)
        
        # Get panorama name
        panorama_name = self.panorama_name_edit.text().strip()
        if not panorama_name:
            panorama_name = "panorama"
        
        # Display result
        if os.path.exists(f'{panorama_name}.jpg'):
            pixmap = QPixmap(f'{panorama_name}.jpg')
            scaled_pixmap = pixmap.scaled(
                self.preview_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
        
        QMessageBox.information(self, "Complete", "Panorama generation completed!")

    # Handle processing errors
    def processing_error(self, error_msg):
        self.get_keyframes_btn.setEnabled(True)
        self.select_video_btn.setEnabled(True)
        self.browse_keyframes_btn.setEnabled(True)
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"An error occurred: {error_msg}")

    # Reset all UI elements to their initial state
    def reset_ui(self):
        # Reset video selection
        self.video_path = None
        self.video_label.setText("No video selected")
        
        # Reset parameters
        self.stride_spin.setValue(10)
        self.panorama_name_edit.clear()
        
        # Reset buttons state
        self.get_keyframes_btn.setEnabled(False)
        self.browse_keyframes_btn.setEnabled(False)
        self.generate_btn.setEnabled(False)
        
        # Reset progress bar
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        
        # Clear preview
        self.preview_label.clear()
        
        # Terminate any running processes
        if self.processor and self.processor.isRunning():
            self.processor.terminate()
        if self.panorama_generator and self.panorama_generator.isRunning():
            self.panorama_generator.terminate()
        
        self.processor = None
        self.panorama_generator = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 