# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('D:\\\\test\\\\ForFM\\\\DataMatrixPrint\\\\.venv\\\\Lib\\\\site-packages\\\\pypdfium2_raw\\\\pdfium.dll', '.'), ('D:\\\\test\\\\ForFM\\\\DataMatrixPrint\\\\.venv\\\\Lib\\\\site-packages\\\\pylibdmtx\\\\libdmtx-64.dll', '.')],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=True,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [('v', None, 'OPTION')],
    exclude_binaries=True,
    name='label_print',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='label_print',
)
