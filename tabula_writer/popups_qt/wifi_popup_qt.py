# popups_qt/wifi_popup_qt.py
from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout, QInputDialog
from .base_popup_qt import BasePopup
from tabula_writer.utils.wifi_manager import scan_wifi_networks, connect_to_wifi, get_current_connection
from tabula_writer.utils.worker_qt import Worker
from tabula_writer.ui.widgets_qt import NavigableListWidget

class WifiPopup(BasePopup):
    def __init__(self, parent=None):
        super().__init__(theme=parent.theme, parent=parent)
        self.app = parent
        self.setWindowTitle("Wi-Fi Connections")
        self.setMinimumSize(500, 400)

        self.status_label = QLabel("Scanning for networks...")
        self.main_layout.addWidget(self.status_label)

        self.network_list = NavigableListWidget()
        self.network_list.itemDoubleClicked.connect(self.connect_to_selected)
        self.main_layout.addWidget(self.network_list)
        
        self.refresh_button = QPushButton("Refresh Scan")
        self.refresh_button.clicked.connect(self.start_scan)
        self.main_layout.addWidget(self.refresh_button)
        
        self.start_scan()
        
    def start_scan(self):
        self.network_list.clear()
        self.status_label.setText("Scanning...")
        self.refresh_button.setEnabled(False)
        worker = Worker(scan_wifi_networks)
        worker.signals.result.connect(self.scan_finished)
        self.app.threadpool.start(worker)

    def scan_finished(self, networks):
        self.refresh_button.setEnabled(True)
        current_ssid = get_current_connection()
        
        if not networks:
            self.status_label.setText("No networks found.")
            return
            
        for net in networks:
            display_text = f"{net['ssid']} ({net['signal']}%)"
            if net['ssid'] == current_ssid:
                display_text += " ✨ Connected"
            self.network_list.addItem(display_text)
            self.network_list.item(self.network_list.count() - 1).setData(1, net)
        
        self.status_label.setText(f"Found {len(networks)} networks.")

    def connect_to_selected(self, item):
        net = item.data(1)
        password = None
        if net['security'] not in ('', 'open'):
            password, ok = QInputDialog.getText(self, "Password Required", f"Enter password for {net['ssid']}:", QLineEdit.EchoMode.Password)
            if not ok: return

        self.status_label.setText(f"Connecting to {net['ssid']}...")
        worker = Worker(connect_to_wifi, net['ssid'], password)
        worker.signals.result.connect(self.connection_finished)
        self.app.threadpool.start(worker)

    def connection_finished(self, result):
        success, message = result
        self.status_label.setText(message)
        if success:
            self.start_scan()
