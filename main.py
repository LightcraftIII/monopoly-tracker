import tkinter as tk
from gui.main_window import MonopolyGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = MonopolyGUI(root)
    root.mainloop()