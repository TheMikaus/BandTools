# PyInstaller spec file for PolyRhythmMetronome
# Build with: pyinstaller Poly_Rhythm_Metronome.spec

import os
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Collect hidden imports
hiddenimports = ['numpy', 'numpy.core._methods', 'numpy.lib.format']

# Try to add optional audio libraries
try:
    hiddenimports += collect_submodules('sounddevice')
except:
    pass

try:
    hiddenimports += ['simpleaudio']
except:
    pass

# Data files to include
datas = []

# Include ticks folder
if os.path.exists('ticks'):
    datas.append(('ticks', 'ticks'))

# Include docs if they exist
if os.path.exists('docs'):
    datas.append(('docs', 'docs'))

# Include README
if os.path.exists('README.md'):
    datas.append(('README.md', '.'))

# Include CHANGELOG
if os.path.exists('CHANGELOG.md'):
    datas.append(('CHANGELOG.md', '.'))

a = Analysis(
    ['Poly_Rhythm_Metronome.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PolyRhythmMetronome',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
