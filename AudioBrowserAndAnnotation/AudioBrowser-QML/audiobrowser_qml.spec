# audiobrowser_qml.spec

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

block_cipher = None

app_script = 'main.py'

# Collect all PyQt6 submodules including QML
hiddenimports = collect_submodules('PyQt6')
hiddenimports += collect_submodules('PyQt6.QtQml')
hiddenimports += collect_submodules('PyQt6.QtQuick')

# Collect PyQt6 data files
datas = collect_data_files('PyQt6', include_py_files=False)

# Include QML files
import os
if os.path.exists('qml'):
    datas += [('qml', 'qml')]

# Include backend modules
if os.path.exists('backend'):
    for root, dirs, files in os.walk('backend'):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, '.')
                datas += [(full_path, rel_path)]

# Include documentation folder
if os.path.exists('docs'):
    datas += [('docs', 'docs')]

# Include README
if os.path.exists('README.md'):
    datas += [('README.md', '.')]

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
    name='AudioBrowser-QML',
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
)
