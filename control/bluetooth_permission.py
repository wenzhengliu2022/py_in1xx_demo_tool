import subprocess
import sys
import platform
try:
    if sys.platform == 'darwin':
        from Foundation import NSBundle
except Exception as e:
    print(str(e))


class BluetoothPermissionManager:
    def __init__(self):
        self.bluetooth_permission_granted = False

    @staticmethod
    def check_bluetooth_permission():
        if sys.platform != 'darwin':
            return True
        try:
            result = subprocess.run([
                'osascript', '-e',
                'tell application "System Events" to get Bluetooth authorization status'
            ], capture_output=True, text=True)

            return "authorized" in result.stdout.lower()

        except Exception as e:
            print(f"check_bluetooth_permission: {e}")
            return False

    @staticmethod
    def request_bluetooth_permission():
        if sys.platform != 'darwin':
            return True
        try:
            # 尝试访问蓝牙服务来触发系统权限对话框
            script = '''
            tell application "System Events"
                try
                    get Bluetooth authorization status
                    return "success"
                on error
                    return "error"
                end try
            end tell
            '''

            result = subprocess.run([
                'osascript', '-e', script
            ], capture_output=True, text=True, timeout=30)

            return "success" in result.stdout

        except subprocess.TimeoutExpired:
            print("request_bluetooth_permission timeout")
            return False
        except Exception as e:
            print(f"request_bluetooth_permission error: {e}")
            return False