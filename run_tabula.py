#!/usr/bin/env python3
import os
import sys

def main():
    # This is the crucial part: it finds where the 'tabula_writer' package
    # was installed and adds its parent directory to the system path.
    try:
        import tabula_writer
        # The 'lib' or 'site-packages' directory
        install_path = os.path.dirname(os.path.dirname(os.path.abspath(tabula_writer.__file__)))
        if install_path not in sys.path:
            sys.path.insert(0, install_path)
    except ImportError:
        # Fallback for running the script directly during development
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

    # Now that the path is guaranteed to be correct, we can import and run the app.
    from tabula_writer.main_qt import main as app_main
    sys.exit(app_main())

if __name__ == '__main__':
    main()
