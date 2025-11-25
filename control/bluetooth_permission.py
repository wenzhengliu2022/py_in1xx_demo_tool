class BluetoothPermissionManager:
    def __init__(self):
        self.bluetooth_permission_granted = False

    @staticmethod
    def check_bluetooth_permission():
        return True

    @staticmethod
    def request_bluetooth_permission():
        return True
