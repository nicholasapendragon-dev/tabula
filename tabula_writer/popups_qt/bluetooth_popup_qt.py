# popups_qt/bluetooth_popup_qt.py
from PyQt6.QtWidgets import QLabel, QPushButton
from .base_popup_qt import BasePopup
from tabula_writer.utils.bluetooth_manager import scan_bluetooth_devices, pair_trust_connect_device
from tabula_writer.utils.worker_qt import Worker
from tabula_writer.ui.widgets_qt import NavigableListWidget

class BluetoothPopup(BasePopup):
    def __init__(self, parent=None):
        super().__init__(theme=parent.theme, parent=parent)
        self.app = parent
        self.setWindowTitle("Bluetooth Connections")
        self.setMinimumSize(500, 400)

        self.status_label = QLabel("Scanning for devices...")
        self.main_layout.addWidget(self.status_label)

        self.device_list = NavigableListWidget()
        self.device_list.itemDoubleClicked.connect(self.connect_to_selected)
        self.main_layout.addWidget(self.device_list)
        
        self.refresh_button = QPushButton("Refresh Scan")
        self.refresh_button.clicked.connect(self.start_scan)
        self.main_layout.addWidget(self.refresh_button)
        
        self.start_scan()
        
    def start_scan(self):
        self.device_list.clear()
        self.status_label.setText("Scanning...")
        self.refresh_button.setEnabled(False)
        worker = Worker(scan_bluetooth_devices)
        worker.signals.result.connect(self.scan_finished)
        self.app.threadpool.start(worker)

    def scan_finished(self, devices):
        self.refresh_button.setEnabled(True)
        if not devices:
            self.status_label.setText("No devices found.")
            return
            
        for dev in devices:
            self.device_list.addItem(f"{dev['name']} ({dev['mac_address']})")
            self.device_list.item(self.device_list.count() - 1).setData(1, dev['mac_address'])
        
        self.status_label.setText(f"Found {len(devices)} devices.")

    def connect_to_selected(self, item):
        mac_address = item.data(1)
        self.status_label.setText(f"Connecting to {mac_address}...")
        worker = Worker(pair_trust_connect_device, mac_address)
        worker.signals.result.connect(self.connection_finished)
        self.app.threadpool.start(worker)

    def connection_finished(self, result):
        _, message = result
        self.status_label.setText(message)
