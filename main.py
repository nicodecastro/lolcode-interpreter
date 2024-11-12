# LOLCODE Interpreter
# AUTHOR: John Nico T. De Castro
# CREATION DATE: 11/12/2024
# DESCRIPTION: An interpreter for the LOLCODE language. A project for CMSC 124.

import tkinter as tk
import os

class LolcodeInterpreterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LOLCODE Interpreter")
        self.root.state("zoomed")
        self.root.resizable(width=False, height=False)
        self.setup_gui()

    def setup_gui(self):
        upper_frame = tk.Frame(self.root, background='blue', height=200, width=800)
        upper_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        execute_frame = tk.Frame(self.root, background='red', height=50, width=800, padx=5, pady=10)
        execute_frame.pack(side=tk.TOP, fill=tk.X)

        execute_button = tk.Button(execute_frame, text="EXECUTE", command=None, background="light gray")
        execute_button.pack(side=tk.TOP, fill=tk.X)

        console_frame = tk.Frame(self.root, background='green', height=100, width=800)
        console_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

root = tk.Tk()
app = LolcodeInterpreterApp(root)
root.mainloop()