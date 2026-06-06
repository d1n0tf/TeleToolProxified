from pystyle import Write, Colors, Colorate
from colorama import *

banner = """
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃                                                                              ┃
    ┃   ████████╗███████╗██╗     ███████╗    ████████╗ ██████╗  ██████╗ ██╗        ┃
    ┃   ╚══██╔══╝██╔════╝██║     ██╔════╝    ╚══██╔══╝██╔═══██╗██╔═══██╗██║        ┃
    ┃      ██║   █████╗  ██║     █████╗         ██║   ██║   ██║██║   ██║██║        ┃
    ┃      ██║   ██╔══╝  ██║     ██╔══╝         ██║   ██║   ██║██║   ██║██║        ┃
    ┃      ██║   ███████╗███████╗███████╗       ██║   ╚██████╔╝╚██████╔╝███████╗   ┃
    ┃      ╚═╝   ╚══════╝╚══════╝╚══════╝       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝   ┃
    ┃                                                                              ┃
    ┃    • TELE TOOL PROXIFIED v1.0 • Created by @klintxxxgod • Fork by @d1n0tf    ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

def print_separator():
    Write.Print("    ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌\n",
                Colors.blue_to_cyan, interval=0.0005)
    
def print_menu_item(num, text, description=""):
    Write.Print(f"    ┃ {num} ┃ {text:<28}", Colors.cyan_to_blue, interval=0.0005)
    if description:
        Write.Print(f" • {description}\n", Colors.blue_to_cyan, interval=0.0005)
    else:
        print()

def print_header(title):
    Write.Print(f"\n    ┏━━ {title} ", Colors.cyan, interval=0.0005)
    Write.Print("━"*(45-len(title)) + "\n", Colors.cyan, interval=0.0005)