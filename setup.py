"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['dicom2nii.py']
DATA_FILES = []
OPTIONS = {
    "iconfile": "Dicom2nii.icns"
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
