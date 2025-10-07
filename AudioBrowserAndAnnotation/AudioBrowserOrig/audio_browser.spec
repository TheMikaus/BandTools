# audio_browser.spec

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

block_cipher = None

app_script = 'audio_browser.py'
hiddenimports = collect_submodules('PyQt6')
datas = collect_data_files('PyQt6', include_py_files=False)

# Include our runtime window icon (PNG). The .ico is used only at build-time for the exe icon.
datas += [('app_icon.png', '.')]

# Include documentation folder
import os
if os.path.exists('docs'):
    datas += [('docs', 'docs')]

a = Analysis(
    [app_script],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='AudioAnnotationBrowser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',   # <— executable icon
)
