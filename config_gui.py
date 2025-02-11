import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

class ConfigManager:
    def __init__(self, use_gui=True):
        self.use_gui = use_gui
        if use_gui:
            self.setup_gui()

try:
    if use_gui:
        self.root = tk.Tk()
        self.root.attributes('-topmost', 1)  # Force window on top
        self.root.after(100, lambda: self.root.attributes('-topmost', 0))
        self.root.title("XScraper Config")
        self.setup_gui()
        self.root.mainloop()
    else:
        self.create_config_cli()

except tk.TclError as e:
    print(f"GUI failed: {str(e)}")
    self.use_gui = False
    self.create_config_cli()