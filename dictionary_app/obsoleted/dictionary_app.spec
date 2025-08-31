# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Dictionary App
Creates a single-file executable with all dependencies bundled
"""

import os
import sys
from pathlib import Path

# Get the absolute path to the app directory
app_dir = Path(os.path.abspath(SPECPATH))

block_cipher = None

# Collect all data files
datas = [
    # Database and data files (include all data files)
    ('data', 'data'),
    
    # Configuration files
    ('config/default_config.json', 'config'),
    ('.env.example', '.'),
    
    # Plugin directories (entire plugin system)
    ('plugins', 'plugins'),
]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'sqlite3',
    'json',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'customtkinter',
    'pystray',
    'PIL',
    'PIL.Image',
    'pynput',
    'pynput.keyboard',
    'keyring',
    'keyring.backends',
    'watchdog',
    'watchdog.observers',
    'watchdog.events',
    'threading',
    'queue',
    'hashlib',
    'platform',
    'uuid',
    'webbrowser',
    'urllib',
    'urllib.request',
]

# Analysis configuration
a = Analysis(
    ['run_app.py'],
    pathex=[str(app_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'pytest',
        'black',
        'mypy',
        'flake8',
        'ipython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove unnecessary binaries
a.binaries = [b for b in a.binaries if not b[0].startswith('matplotlib')]
a.binaries = [b for b in a.binaries if not b[0].startswith('numpy')]

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# Executable configuration
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DictionaryApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='assets/icon.ico'  # Add icon file when available
)

# For macOS, create an app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='DictionaryApp.app',
        # icon='assets/icon.icns',  # macOS icon
        bundle_identifier='com.dictionaryapp.app',
        info_plist={
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.15.0',
        }
    )