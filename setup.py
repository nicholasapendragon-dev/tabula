from setuptools import setup, find_packages
import os

# Function to read the contents of your README file
def read_readme():
    return open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

setup(
    name='tabula-writer',
    version='0.1.0', # Start with 0.1.0, you can increment this for releases
    author='Nicholas A. Pendragon-Dev',
    author_email='Nicholasapendragon@gmail.com',
    description='A distraction-free writing environment for Raspberry Pi',
    long_description=read_readme() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    url='https://github.com/nicholasapendragon-dev/tabula',
    packages=find_packages(), # Automatically find all packages in the directory
    include_package_data=True, # Include non-code files specified in MANIFEST.in or package_data
    install_requires=[
        'PyQt6',
        'python-dotenv',
        'python-docx',
        'markdown',
        'PyPDF2', # For PDF export if you're using it this way
        'whoosh', # For search indexing
        'beautifulsoup4', # Often used with markdown or HTML parsing
        'requests', # For any web requests, e.g., weather/API integration (if planned)
        'pypdf' # Modern PDF library
        # Add any other Python dependencies your project uses here
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
        'Environment :: X11 Applications :: Qt',
        'License :: OSI Approved :: MIT License', # Or whatever license you choose
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Office/Business :: Word Processors',
    ],
    entry_points={
        'gui_scripts': [
            'tabula = tabula_writer.main_qt:main', # Makes 'tabula' runnable from terminal
        ],
    },
)
