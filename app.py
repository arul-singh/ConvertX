import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QComboBox, QTextEdit, 
                             QFileDialog, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent

class DragDropArea(QFrame):
    """Custom visual card widget handling cross-platform desktop drag-and-drop events."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setAcceptDrops(True)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        # Premium Dark Palette Styling
        self.setStyleSheet("""
            QFrame {
                background-color: #121214;
                border: 2px dashed #2C2C2E;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        self.label = QLabel("DRAG & DROP FILES HERE\nOR CLICK 'ADD FILES' BELOW", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: #8E8E93; font-family: 'Helvetica Neue'; font-size: 12px; font-weight: bold;")
        layout.addWidget(self.label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            self.setStyleSheet("""
                QFrame {
                    background-color: #1C1C1E;
                    border: 2px dashed #3498DB;
                    border-radius: 12px;
                }
            """)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QFrame {
                background-color: #121214;
                border: 2px dashed #2C2C2E;
                border-radius: 12px;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("""
            QFrame {
                background-color: #121214;
                border: 2px dashed #2C2C2E;
                border-radius: 12px;
            }
        """)
        urls = event.mimeData().urls()
        if urls:
            file_paths = [url.toLocalFile() for url in urls if os.path.exists(url.toLocalFile())]
            self.parent.add_files_to_queue(file_paths)
            event.acceptProposedAction()


class ConvertXStudio(QWidget):
    def __init__(self):
        super().__init__()
        self.input_files = []
        self.output_dir = None
        
        self.FORMAT_MAP = {
            "docs": ["docx", "pdf", "odt", "rtf", "txt", "html", "epub", "mobi", "fb2"],
            "markup": ["md", "gfm", "tex", "rst", "asciidoc", "ipynb", "org", "wiki", "json", "xml", "csv", "tsv"],
            "images": ["png", "jpg", "jpeg", "webp", "bmp", "gif", "tiff", "ico"],
            "audio": ["mp3", "wav", "m4a", "flac", "ogg", "aac"],
            "video": ["mp4", "mkv", "avi", "mov", "webm", "flv"]
        }
        self.ALL_FORMATS = sorted(list(set(sum(self.FORMAT_MAP.values(), []))))
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("ConvertX Studio Pro")
        self.setFixedSize(680, 640)
        self.setStyleSheet("background-color: #0A0A0A; color: #FFFFFF;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(15)

        # --- HEADER ---
        header_layout = QVBoxLayout()
        lbl_title = QLabel("CONVERTX STUDIO", self)
        lbl_title.setStyleSheet("font-family: 'Helvetica Neue'; font-size: 26px; font-weight: bold; color: #FFFFFF;")
        lbl_subtitle = QLabel("Smart Multi-Platform Conversion Hub", self)
        lbl_subtitle.setStyleSheet("font-family: 'Helvetica Neue'; font-size: 12px; color: #7F8C8D;")
        header_layout.addWidget(lbl_title)
        header_layout.addWidget(lbl_subtitle)
        main_layout.addLayout(header_layout)

        # --- DRAG AND DROP ZONE ---
        self.drop_area = DragDropArea(self)
        self.drop_area.setFixedHeight(90)
        main_layout.addWidget(self.drop_area)

        # --- QUEUE DISPLAY BOX ---
        self.queue_box = QTextEdit(self)
        self.queue_box.setReadOnly(True)
        self.queue_box.setFixedHeight(120)
        self.queue_box.setStyleSheet("""
            QTextEdit {
                background-color: #1C1C1E;
                border: 1px solid #2C2C2E;
                border-radius: 8px;
                color: #8E8E93;
                font-family: 'Courier';
                font-size: 12px;
                padding: 8px;
            }
        """)
        self.queue_box.setPlaceholderText("Staging Queue Empty.\nDrop items above or use 'Add Files' below...")
        main_layout.addWidget(self.queue_box)

        # --- QUEUE ACTIONS ---
        queue_btns = QHBoxLayout()
        self.btn_clear = QPushButton("Clear Queue", self)
        self.btn_clear.setStyleSheet("background-color: #C0392B; color: white; border-radius: 6px; padding: 6px; font-size: 12px;")
        self.btn_clear.clicked.connect(self.clear_queue)
        
        self.btn_add = QPushButton("Add Files...", self)
        self.btn_add.setStyleSheet("background-color: #34495E; color: white; border-radius: 6px; padding: 6px 15px; font-size: 12px; font-weight: bold;")
        self.btn_add.clicked.connect(self.browse_files)
        
        queue_btns.addWidget(self.btn_clear)
        queue_btns.addStretch()
        queue_btns.addWidget(self.btn_add)
        main_layout.addLayout(queue_btns)

        # --- CONFIGURATION MATRIX CARD ---
        config_card = QFrame(self)
        config_card.setStyleSheet("background-color: #1C1C1E; border: 1px solid #2C2C2E; border-radius: 12px;")
        config_layout = QVBoxLayout(config_card)
        config_layout.setContentsMargins(20, 15, 20, 15)
        
        lbl_target = QLabel("TARGET EXTENSION FORMAT (AUTO-FILTERED)", self)
        lbl_target.setStyleSheet("font-family: 'Helvetica Neue'; font-size: 10px; font-weight: bold; color: #A2A2A6; border: none;")
        self.combo_target = QComboBox(self)
        self.combo_target.addItems(self.ALL_FORMATS)
        self.combo_target.setCurrentText("docx")
        self.combo_target.setStyleSheet("""
            QComboBox {
                background-color: #2A2A2E;
                border: 1px solid #3A3A3E;
                border-radius: 6px;
                padding: 6px;
                color: white;
            }
            QComboBox::drop-down { border: none; }
        """)
        config_layout.addWidget(lbl_target)
        config_layout.addWidget(self.combo_target)
        main_layout.addWidget(config_card)

        # --- DESTINATION CARD ---
        dest_card = QFrame(self)
        dest_card.setStyleSheet("background-color: #1C1C1E; border: 1px solid #2C2C2E; border-radius: 12px;")
        dest_layout = QVBoxLayout(dest_card)
        dest_layout.setContentsMargins(20, 15, 20, 15)
        
        lbl_dest = QLabel("OUTPUT DESTINATION MANAGEMENT", self)
        lbl_dest.setStyleSheet("font-family: 'Helvetica Neue'; font-size: 10px; font-weight: bold; color: #A2A2A6; border: none;")
        self.lbl_dest_path = QLabel("Default: Same folder as source files", self)
        self.lbl_dest_path.setStyleSheet("font-family: 'Helvetica Neue'; font-size: 12px; color: #7F8C8D; border: none; font-style: italic;")
        
        btn_dest = QPushButton("Choose Output Directory...", self)
        btn_dest.setStyleSheet("background-color: #2A2A2E; color: white; border-radius: 6px; padding: 5px 12px; font-size: 12px;")
        btn_dest.clicked.connect(self.choose_output_dir)
        
        dest_upper = QHBoxLayout()
        dest_upper.addWidget(lbl_dest)
        dest_upper.addStretch()
        dest_upper.addWidget(btn_dest)
        
        dest_layout.addLayout(dest_upper)
        dest_layout.addWidget(self.lbl_dest_path)
        main_layout.addWidget(dest_card)

        # --- TRIGGER CONVERSION BUTTON ---
        self.btn_convert = QPushButton("Execute Batch Conversion", self)
        self.btn_convert.setEnabled(False)
        self.btn_convert.setStyleSheet("""
            QPushButton {
                background-color: #107C41;
                color: white;
                font-family: 'Helvetica Neue';
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton:disabled {
                background-color: #1C3A27;
                color: #557A61;
            }
        """)
        self.btn_convert.clicked.connect(self.run_batch_conversion)
        main_layout.addWidget(self.btn_convert)

        # --- STATUS FOOTER ---
        self.lbl_status = QLabel("System Ready", self)
        self.lbl_status.setStyleSheet("font-family: 'Helvetica Neue'; font-size: 12px; color: #7F8C8D;")
        main_layout.addWidget(self.lbl_status)

    def add_files_to_queue(self, paths):
        for path in paths:
            if path not in self.input_files:
                self.input_files.append(path)
        self.update_queue_ui()

    def browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Queue")
        if files:
            self.add_files_to_queue(files)

    def choose_output_dir(self):
        chosen_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if chosen_dir:
            self.output_dir = chosen_dir
            self.lbl_dest_path.setText(f"Custom Destination: {os.path.basename(chosen_dir)}")
            self.lbl_dest_path.setStyleSheet("color: #3498DB; font-style: normal; font-size: 12px;")
        else:
            self.output_dir = None
            self.lbl_dest_path.setText("Default: Same folder as source files")
            self.lbl_dest_path.setStyleSheet("color: #7F8C8D; font-style: italic; font-size: 12px;")

    def clear_queue(self):
        self.input_files = []
        self.update_queue_ui()

    def update_queue_ui(self):
        self.queue_box.clear()
        if not self.input_files:
            self.btn_convert.setEnabled(False)
            self.lbl_status.setText("System Ready")
            self.lbl_status.setStyleSheet("color: #7F8C8D;")
            self.combo_target.clear()
            self.combo_target.addItems(self.ALL_FORMATS)
            self.combo_target.setCurrentText("docx")
        else:
            for idx, f in enumerate(self.input_files, 1):
                self.queue_box.append(f"[{idx}] {os.path.basename(f)}")
            self.btn_convert.setEnabled(True)
            self.lbl_status.setText(f"Loaded {len(self.input_files)} asset(s) into staging queue")
            self.lbl_status.setStyleSheet("color: #2ECC71;")
            self.detect_smart_formats()

    def detect_smart_formats(self):
        detected_groups = set()
        for f in self.input_files:
            ext = os.path.splitext(f)[1].lower().replace(".", "")
            for group_name, extensions in self.FORMAT_MAP.items():
                if ext in extensions:
                    detected_groups.add(group_name)
                    break

        if len(detected_groups) == 1:
            group = list(detected_groups)[0]
            smart_list = self.FORMAT_MAP[group]
        else:
            smart_list = self.ALL_FORMATS
            
        self.combo_target.clear()
        self.combo_target.addItems(smart_list)

    def run_batch_conversion(self):
        target_ext = self.combo_target.currentText()
        total = len(self.input_files)
        success_count = 0
        
        for idx, file_path in enumerate(self.input_files, 1):
            filename = os.path.basename(file_path)
            self.lbl_status.setText(f"Converting ({idx}/{total}): {filename}...")
            self.lbl_status.setStyleSheet("color: #E67E22;")
            QApplication.processEvents() # Keeps UI completely responsive on Windows/Mac/Linux
            
            file_dir, file_name = os.path.split(file_path)
            name_without_ext, src_ext = os.path.splitext(file_name)
            src_ext = src_ext.lower().replace(".", "")
            
            final_dest = self.output_dir if self.output_dir else file_dir
            output_file = os.path.join(final_dest, f"{name_without_ext}.{target_ext}")
            
            try:
                success = False
                if src_ext in self.FORMAT_MAP["images"] and target_ext in self.FORMAT_MAP["images"]:
                    from PIL import Image
                    img = Image.open(file_path)
                    if target_ext in ["jpg", "jpeg"] and img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    img.save(output_file)
                    success = True
                elif src_ext == 'pdf' and target_ext == 'docx':
                    from pdf2docx import Converter
                    cv = Converter(file_path)
                    cv.convert(output_file, start=0, end=None)
                    cv.close()
                    success = True
                elif src_ext in self.FORMAT_MAP["audio"] + self.FORMAT_MAP["video"] and target_ext in self.FORMAT_MAP["audio"] + self.FORMAT_MAP["video"]:
                    cmd = ["ffmpeg", "-i", file_path, "-y", output_file]
                    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    success = (result.returncode == 0)
                else:
                    cmd = ["pandoc", "-s", file_path, "-o", output_file]
                    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    success = (result.returncode == 0)
                
                if success:
                    success_count += 1
            except Exception as e:
                print(f"Conversion error: {e}")

        QMessageBox.information(self, "Batch Complete", f"Successfully converted {success_count}/{total} files to {target_ext.upper()}!")
        self.clear_queue()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    studio = ConvertXStudio()
    studio.show()
    sys.exit(app.exec())