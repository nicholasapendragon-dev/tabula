from setuptools import setup, find_packages
import os

def find_assets(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

asset_files = find_assets('tabula_writer/assets')

setup(
    name='tabula-writer',
    version='2.0.0',
    author='Nicholas Pendragon',
    author_email='nicholasapendragon@gmail.com',
    packages=find_packages(),
    description='A focused academic writing application using PyQt6.',
    install_requires=[
        'python-docx',
        'fpdf2',
        'pyspellchecker',
        'PyQt6'
    ],
    entry_points={
        'gui_scripts': [
            'tabula = tabula_writer.main_qt:main',
        ],
    },
    include_package_data=True,
    package_data={
        'tabula_writer': asset_files,
    },
    zip_safe=False
)
