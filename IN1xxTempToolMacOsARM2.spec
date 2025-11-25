# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('nanobeacon.ico','nanobeacon.ico')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PyTempTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity='Developer ID Application: Ben He (VQ97CV8MX5)',
    entitlements_file=None,
    icon='nanobeacon.icns',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PyTempTool',
)
app = BUNDLE(
    coll,
    name='PyTempTool.app',
    icon='nanobeacon.icns',
    bundle_identifier='com.inplay.temptool',
	info_plist={
                'NSBluetoothAlwaysUsageDescription': 'This app needs access to Bluetooth to scan for devices.',
                'UIBackgroundModes': ['bluetooth-central']
             }
)
