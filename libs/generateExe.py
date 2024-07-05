import subprocess
import sys
import os
from libs.printer import TextPrinter, TextStyle
 

class Generate:
    @staticmethod
    def generateExe():
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # Hiding annoying pygame message
        try:
            import PyInstaller.__main__ # type: ignore
        except ImportError:
            TextPrinter.print("PyInstaller not found. Installing...", TextStyle.BLUE)
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            TextPrinter.print("PyInstaller has been installed.", TextStyle.GREEN)
            import PyInstaller.__main__ # type: ignore

        TextPrinter.print("Generating executable file...", TextStyle.BLUE)
        PyInstaller.__main__.run([
            'main.py',
            '--onefile',
            '--name=openspy',
            '--clean',
            '--distpath', '',
            '--log-level', 'DEPRECATION'
        ])
        TextPrinter.print("openspy.exe has been successfully generated.", TextStyle.GREEN)