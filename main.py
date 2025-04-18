import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QSpinBox, QGroupBox,
                           QFrame, QComboBox, QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from memory_manager import MemoryManager
from visualization import MemoryVisualizer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garbage Collection Visualization")
        self.setMinimumSize(1200, 800)
        
        # Set dark theme colors
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
            }
            QGroupBox {
                color: #ffffff;
                background-color: #3b3b3b;
                border: 2px solid #4a4a4a;
                border-radius: 10px;
                margin-top: 1em;
                padding-top: 1em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #6a6a6a;
            }
            QSpinBox {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #5a5a5a;
                border-radius: 3px;
                padding: 5px;
                min-width: 80px;
            }
            QComboBox {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #5a5a5a;
                border-radius: 3px;
                padding: 5px;
                min-width: 80px;
            }
            QComboBox:hover {
                border: 1px solid #6a6a6a;
            }
            QProgressBar {
                border: 1px solid #5a5a5a;
                border-radius: 5px;
                text-align: center;
                background-color: #3b3b3b;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 4px;
            }
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create title with custom font
        title_label = QLabel("Garbage Collection Visualization")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #3b3b3b;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # Create memory information panel
        memory_info_group = QGroupBox("Memory Information")
        memory_info_layout = QVBoxLayout()
        
        # Create progress bar for memory usage
        self.memory_progress = QProgressBar()
        self.memory_progress.setMinimum(0)
        self.memory_progress.setMaximum(100)
        self.memory_progress.setValue(0)
        self.memory_progress.setStyleSheet("""
            QProgressBar {
                height: 25px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        
        # Create memory stats layout
        memory_stats_layout = QHBoxLayout()
        self.total_memory_label = QLabel("Total Memory: 0 MB")
        self.used_memory_label = QLabel("Used Memory: 0 MB")
        self.free_memory_label = QLabel("Free Memory: 0 MB")
        
        for label in [self.total_memory_label, self.used_memory_label, self.free_memory_label]:
            label.setStyleSheet("""
                QLabel {
                    background-color: #3b3b3b;
                    padding: 8px 15px;
                    border-radius: 5px;
                }
            """)
            memory_stats_layout.addWidget(label)
        
        memory_info_layout.addWidget(self.memory_progress)
        memory_info_layout.addLayout(memory_stats_layout)
        memory_info_group.setLayout(memory_info_layout)
        main_layout.addWidget(memory_info_group)
        
        # Create control panel
        control_group = QGroupBox("Memory Control")
        control_layout = QVBoxLayout()
        
        # Create object size selection
        size_layout = QHBoxLayout()
        size_label = QLabel("Object Size:")
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(1, 1000)
        self.size_spinbox.setValue(100)
        self.size_spinbox.setSuffix(" MB")
        
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["MB", "GB"])
        self.unit_combo.currentTextChanged.connect(self.update_size_range)
        
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_spinbox)
        size_layout.addWidget(self.unit_combo)
        size_layout.addStretch()
        
        # Create preset sizes
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Preset Sizes:")
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["Custom", "Small (10 MB)", "Medium (100 MB)", "Large (500 MB)", "Huge (1 GB)"])
        self.preset_combo.currentTextChanged.connect(self.apply_preset)
        
        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.preset_combo)
        preset_layout.addStretch()
        
        # Create buttons with icons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Object")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        self.gc_button = QPushButton("Run Garbage Collection")
        self.gc_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        
        self.clear_button = QPushButton("Clear Memory")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #c62828;
            }
        """)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.gc_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        
        control_layout.addLayout(size_layout)
        control_layout.addLayout(preset_layout)
        control_layout.addLayout(button_layout)
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)
        
        # Create visualization
        self.visualizer = MemoryVisualizer()
        main_layout.addWidget(self.visualizer)
        
        # Add status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #3b3b3b;
                padding: 8px;
                border-radius: 5px;
                margin-top: 10px;
            }
        """)
        main_layout.addWidget(self.status_label)
        
        # Initialize memory manager
        self.memory_manager = MemoryManager(total_memory=1024)  # 1GB total memory
        
        # Connect signals
        self.add_button.clicked.connect(self.add_object)
        self.gc_button.clicked.connect(self.run_garbage_collection)
        self.clear_button.clicked.connect(self.clear_memory)
        
        # Update initial state
        self.update_memory_info()
        self.update_visualization()

    def update_size_range(self, unit):
        if unit == "MB":
            self.size_spinbox.setRange(1, 1000)
            self.size_spinbox.setSuffix(" MB")
        else:
            self.size_spinbox.setRange(1, 10)
            self.size_spinbox.setSuffix(" GB")

    def apply_preset(self, preset):
        if preset == "Custom":
            return
        size_map = {
            "Small (10 MB)": (10, "MB"),
            "Medium (100 MB)": (100, "MB"),
            "Large (500 MB)": (500, "MB"),
            "Huge (1 GB)": (1, "GB")
        }
        size, unit = size_map[preset]
        self.unit_combo.setCurrentText(unit)
        self.size_spinbox.setValue(size)

    def add_object(self):
        size = self.size_spinbox.value()
        if self.unit_combo.currentText() == "GB":
            size *= 1024  # Convert GB to MB
        if self.memory_manager.allocate_object(size):
            self.update_memory_info()
            self.update_visualization()
        else:
            # Show error message if memory allocation fails
            self.status_label.setText("Failed to allocate memory: Memory full!")

    def run_garbage_collection(self):
        self.memory_manager.run_garbage_collection()
        self.update_memory_info()
        self.update_visualization()

    def clear_memory(self):
        # Reinitialize the memory manager with the same total memory
        total_memory = self.memory_manager.total_memory
        self.memory_manager = MemoryManager(total_memory=total_memory)
        self.update_memory_info()
        self.update_visualization()
        self.status_label.setText("Memory cleared successfully")

    def update_memory_info(self):
        total_memory = self.memory_manager.total_memory
        used_memory = self.memory_manager.used_memory
        free_memory = total_memory - used_memory
        
        self.total_memory_label.setText(f"Total Memory: {self.format_size(total_memory)}")
        self.used_memory_label.setText(f"Used Memory: {self.format_size(used_memory)}")
        self.free_memory_label.setText(f"Free Memory: {self.format_size(free_memory)}")
        
        usage_percentage = (used_memory / total_memory) * 100
        self.memory_progress.setValue(int(usage_percentage))

    def update_visualization(self):
        memory_state = {
            'total_memory': self.memory_manager.total_memory,
            'used_memory': self.memory_manager.used_memory,
            'objects': self.memory_manager.objects,
            'root_objects': self.memory_manager.root_objects
        }
        self.visualizer.update_visualization(memory_state)

    def format_size(self, size_mb):
        if size_mb >= 1024:
            return f"{size_mb/1024:.1f} GB"
        return f"{size_mb} MB"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 