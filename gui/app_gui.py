import time
from collections import deque

import pyqtgraph as pg
from PySide6.QtCore import Qt, QResource
from PySide6.QtGui import QFont, QPixmap, QPalette, QColor
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel

from control.app_config import AppConfig
from control.ble_scan import BLEScannerThread
from control.bluetooth_permission import BluetoothPermissionManager
from gui import images_rc

MAX_DATA_POINTS = 100


# resource_id = QResource.registerResource(images_rc)


class TimeAxisItem(pg.DateAxisItem):
    """A custom axis item that displays time in HH:MM:S format."""

    def tickStrings(self, values, scale, spacing):
        # PySide2 may return float values; we need int for strftime
        return [time.strftime("%H:%M:%S", time.localtime(int(v))) for v in values]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.permission_manager = BluetoothPermissionManager()
        self.setWindowTitle("IN1xx Temperature Tool")
        self.setGeometry(100, 100, 1000, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.temp_label = QLabel()
        palette1 = self.temp_label.palette()
        palette1.setColor(QPalette.Window, QColor(255, 255, 255))
        palette1.setColor(QPalette.WindowText, QColor(0, 0, 0))
        self.temp_label.setAutoFillBackground(True)
        self.temp_label.setPalette(palette1)

        # self.temp_label.setText("BLE Scanning ...")

        self.temp_label.setAlignment(Qt.AlignCenter)
        self.temp_label.setFont(QFont("Arial", 60, QFont.Bold))
        self.layout.addWidget(self.temp_label)

        # Use custom TimeAxisItem
        self.plot_widget = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.plot_widget.getPlotItem().getViewBox().enableAutoRange(axis='y', enable=False)
        self.plot_widget.setYRange(-20, 40)
        self.layout.addWidget(self.plot_widget)
        self.plot_widget.setBackground('w')
        self.plot_widget.setTitle("Temperature Curve", color="k", size="16pt")
        styles = {"color": "k", "font-size": "12pt"}
        self.plot_widget.setLabel("left", "Temperature (°C)", **styles)
        self.plot_widget.setLabel("bottom", "Time", **styles)
        self.plot_widget.showGrid(x=True, y=True)
        self.pen = pg.mkPen(color=(255, 0, 0), width=2)
        self.data_line = self.plot_widget.plot([], [], pen=self.pen)

        self.time_data = deque(maxlen=MAX_DATA_POINTS)
        self.temp_data = deque(maxlen=MAX_DATA_POINTS)
        self.sample_count = 0
        self.config = AppConfig("IN1xxTempTool")
        self.scanner_thread = BLEScannerThread(self.config)
        # self.scanner_thread.newData.connect(self.update_ui)
        # self.scanner_thread.start()

        self.check_permissions_on_start()

    def check_permissions_on_start(self):
        if self.permission_manager.check_bluetooth_permission():
            self.on_permission_granted()
        else:
            self.on_permission_denied()

    def on_permission_granted(self):
        self.temp_label.setText("BLE Scanning ...")
        self.scanner_thread.newData.connect(self.update_ui)
        self.scanner_thread.start()

    def on_permission_denied(self):
        self.temp_label.setText("✗ Bluetooth permission denied")

    def update_ui(self, temperature: float):
        html_text = f"{temperature:.1f} <img src=':/image/images/temperature_64x64.png' width='64' height='64'>"
        # self.temp_label.setText(f"{temperature:.2f} °C")
        self.temp_label.setText(html_text)

        self.time_data.append(time.time())
        self.temp_data.append(temperature)
        self.sample_count += 1

        self.data_line.setData(list(self.time_data), list(self.temp_data), symbol='o', symbolSize=6)

    def closeEvent(self, event):
        print("closeEvent")
        if self.scanner_thread.isRunning():
            self.scanner_thread.stop_scan()
            self.scanner_thread.quit()
            self.scanner_thread.wait()
        event.accept()
