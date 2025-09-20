# popups_qt/email_popup_qt.py
from PyQt6.QtWidgets import (QLabel, QLineEdit, QTextEdit, QPushButton, QRadioButton, 
                             QGridLayout, QButtonGroup, QFrame, QHBoxLayout)
from .base_popup_qt import BasePopup
from tabula_writer.ui.widgets_qt import NavigableRadioButton

class EmailPopup(BasePopup):
    def __init__(self, doc_name, saved_config, parent=None):
        super().__init__(theme=parent.theme, parent=parent)
        self.saved_config = saved_config
        self.setWindowTitle("Email Document")
        
        layout = QGridLayout()
        layout.setSpacing(10)
        
        self.to_edit = self._add_row(layout, 0, "To:", QLineEdit(), self.saved_config.get('to', ''))
        self.subject_edit = self._add_row(layout, 1, "Subject:", QLineEdit(), self.saved_config.get('subject', doc_name))
        
        layout.addWidget(QLabel("Body:"), 2, 0)
        self.body_edit = QTextEdit()
        self.body_edit.setPlainText(self.saved_config.get('body', f"Please find '{doc_name}' attached."))
        layout.addWidget(self.body_edit, 2, 1, 1, 2)
        
        self.smtp_server_edit = self._add_row(layout, 3, "SMTP Server:", QLineEdit(), self.saved_config.get('smtp_server', ''))
        self.port_edit = self._add_row(layout, 4, "Port:", QLineEdit(), self.saved_config.get('port', '587'))
        self.username_edit = self._add_row(layout, 5, "Username:", QLineEdit(), self.saved_config.get('username', ''))
        self.password_edit = self._add_row(layout, 6, "Password:", QLineEdit(), self.saved_config.get('password', ''))
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        
        format_frame = QFrame()
        format_layout = QHBoxLayout(format_frame)
        format_layout.setContentsMargins(0,0,0,0)
        format_layout.addWidget(QLabel("Send as:"))
        self.button_group = QButtonGroup()
        
        self.pdf_button = NavigableRadioButton("PDF")
        self.pdf_button.setChecked(True)
        self.docx_button = NavigableRadioButton("DOCX")
        self.txt_button = NavigableRadioButton("TXT")
        
        self.button_group.addButton(self.pdf_button)
        self.button_group.addButton(self.docx_button)
        self.button_group.addButton(self.txt_button)
        
        format_layout.addWidget(self.pdf_button)
        format_layout.addWidget(self.docx_button)
        format_layout.addWidget(self.txt_button)
        format_layout.addStretch()
        
        self.send_button = QPushButton("Send")
        self.send_button.setObjectName("GreenButton")
        self.send_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        format_layout.addWidget(self.cancel_button)
        format_layout.addWidget(self.send_button)

        self.main_layout.addLayout(layout)
        self.main_layout.addWidget(format_frame)

    def _add_row(self, layout, row, label_text, widget, default_text=""):
        layout.addWidget(QLabel(label_text), row, 0)
        widget.setText(default_text)
        layout.addWidget(widget, row, 1, 1, 2)
        return widget

    def get_details(self):
        send_as = 'pdf'
        if self.docx_button.isChecked(): send_as = 'docx'
        elif self.txt_button.isChecked(): send_as = 'txt'
            
        details = {
            'to': self.to_edit.text(), 'subject': self.subject_edit.text(), 'body': self.body_edit.toPlainText(),
            'smtp_server': self.smtp_server_edit.text(), 'port': self.port_edit.text(),
            'username': self.username_edit.text(), 'password': self.password_edit.text(), 'send_as': send_as
        }
        self.parent().config['email_config'] = {k: v for k, v in details.items() if k != 'password'}
        self.parent().config['email_config']['body'] = "" # Don't save body
        self.parent().save_config(self.parent().config)
        return details
