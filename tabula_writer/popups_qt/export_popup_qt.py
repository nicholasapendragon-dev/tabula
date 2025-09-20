# popups_qt/export_popup_qt.py
from PyQt6.QtWidgets import QLabel, QPushButton, QRadioButton, QHBoxLayout, QButtonGroup, QFrame
from .base_popup_qt import BasePopup
from tabula_writer.ui.widgets_qt import NavigableRadioButton

class ExportPopup(BasePopup):
    def __init__(self, document_name, parent=None):
        super().__init__(theme=parent.theme, parent=parent)

        self.setWindowTitle("Export Document")

        label = QLabel(f"Export '<b>{document_name}</b>' as:")
        self.main_layout.addWidget(label)

        self.button_group = QButtonGroup(self)
        
        self.docx_button = NavigableRadioButton("Microsoft Word (.docx)")
        self.docx_button.setChecked(True)
        self.button_group.addButton(self.docx_button)
        self.main_layout.addWidget(self.docx_button)
        
        self.pdf_button = NavigableRadioButton("PDF Document (.pdf)")
        self.button_group.addButton(self.pdf_button)
        self.main_layout.addWidget(self.pdf_button)

        button_container = QFrame()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        self.export_button = QPushButton("Export")
        self.export_button.setObjectName("GreenButton")
        self.export_button.clicked.connect(self.accept)
        self.export_button.setDefault(True)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.export_button)
        
        self.main_layout.addWidget(button_container)

    def get_selected_format(self):
        return "docx" if self.docx_button.isChecked() else "pdf"
