from enum import Enum
import os

class TextStyle(Enum):
    BOLD = 'Bold'
    HEADER = 'Header'
    WARNING = 'Warning'
    ARGUMENT = 'Cyan'
    ERROR = 'Fail'
    GRAY = 'Gray'
    BLUE = 'Blue'
    GREEN = 'Green'
    RED = 'Red'


class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    GRAY = '\033[90m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED = '\033[91m'

class TextPrinter:
    @staticmethod
    def print(text: str, style: TextStyle = None):
        if not style:
            print(text)
            return
        
        color_code = getattr(bcolors, style.name, '')
        print(color_code + text + bcolors.ENDC)

    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def input():
        return input('\n\033[92m' + '> ' + '\033[0m')
    
    @staticmethod
    def guide(message: str):
        print(bcolors.GRAY + '\u2139 ' + message + bcolors.ENDC)
