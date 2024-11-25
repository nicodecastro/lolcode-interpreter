# LOLCODE Interpreter
# AUTHOR: John Nico T. De Castro
# CREATION DATE: 11/12/2024
# DESCRIPTION: An interpreter for the LOLCODE language. A project for CMSC 124.

'''
TODO:
Important, Urgent
- Lexemes in line not in order, esp. nested
- VISIBLE concatenation separated by +
- Function Identifier
- Function parameters
- Loop identifier
- OBTW & TLDR

Important, Not Urgent
- Writing file when no file selected
'''

import customtkinter as ctk
import tkinter.ttk as ttk
import os
import lexical_analyzer as la

class LolcodeInterpreterApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self._state_before_windows_set_titlebar_color = 'zoomed'
        self.title("LOLCODE Interpreter")
        self.resizable(width=False, height=False)
        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=200)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=100)

        self.lolcode_source = None
        self.tokens = []

        self.setup_gui()

        # self.load_testcase()    # TODO: FOR TESTING PURPOSES ONLY, REMOVE

    def load_testcase(self) -> None:    # TODO: FOR TESTING PURPOSES ONLY, REMOVE
        selected_file = os.path.join(os.getcwd(), "tests", "lolcode-files", "01_variables.lol")
        self.current_filepath = selected_file
        self.current_filename.set(os.path.basename(selected_file))
        file = open(self.current_filepath, 'r')
        self.lolcode_source = file.read()
        file.close()
        self.text_editor.insert(ctk.END, self.lolcode_source)

    def setup_gui(self) -> None:
        # Upper Left Frame
        upper_left_frame = ctk.CTkFrame(self)
        upper_left_frame.grid(column=0, row=0, sticky="nsew")
        upper_left_frame.grid_columnconfigure(0, weight=1)
        upper_left_frame.grid_rowconfigure(0, weight=1)
        upper_left_frame.grid_rowconfigure(1, weight=200)

        # file_explorer
        self.current_filepath = None
        self.current_filename = ctk.StringVar(upper_left_frame, value="(None)")
        file_explorer_button = ctk.CTkButton(upper_left_frame, textvariable=self.current_filename, height=15, command=self.select_file, anchor="w")
        file_explorer_button.grid(column=0, row=0, sticky="nsew",pady=(0, 5))

        # text editor
        self.text_editor = ctk.CTkTextbox(upper_left_frame, undo=True)
        self.text_editor.grid(column=0, row=1, sticky="nsew")
        
        # Upper Mid Frame
        upper_mid_frame = ctk.CTkFrame(self)
        upper_mid_frame.grid(column=1, row=0, sticky="nsew")
        upper_mid_frame.grid_columnconfigure(0, weight=1)
        upper_mid_frame.grid_rowconfigure(0, weight=1)
        upper_mid_frame.grid_rowconfigure(1, weight=100)

        # Lexeme Table Label
        token_table_label = ctk.CTkLabel(upper_mid_frame, text="Lexemes", height=15, pady=5)
        token_table_label.grid(column=0, row=0, sticky="nsew")

        # Lexeme Table
        token_table_frame = ctk.CTkFrame(upper_mid_frame, fg_color='green')
        token_table_frame.grid(column=0, row=1, sticky="nsew")
        token_table_frame.grid_columnconfigure(0, weight=1)
        token_table_frame.grid_rowconfigure(0, weight=1)

        self.token_table = ttk.Treeview(token_table_frame, columns=("Lexeme", "Classification"), show="headings")
        self.token_table.grid(column=0, row=0, sticky="nsew")
        self.token_table.column("#1", anchor=ctk.CENTER)
        self.token_table.heading("#1", text="Lexeme")
        self.token_table.column("#2", anchor=ctk.CENTER)
        self.token_table.heading("#2", text="Classification")

        token_table_scrollbar = ttk.Scrollbar(token_table_frame, orient="vertical", command=self.token_table.yview)
        self.token_table.configure(yscroll=token_table_scrollbar.set)
        token_table_scrollbar.grid(column=1, row=0, sticky="ns")

        # Upper Right Frame
        upper_right_frame = ctk.CTkFrame(self)
        upper_right_frame.grid(column=2, row=0, sticky="nsew")
        upper_right_frame.grid_columnconfigure(0, weight=1)
        upper_right_frame.grid_rowconfigure(0, weight=1)
        upper_right_frame.grid_rowconfigure(1, weight=100)

        # Symbol Table Label
        symbol_table_label = ctk.CTkLabel(upper_right_frame, text="Symbol Table", height=15, pady=5)
        symbol_table_label.grid(column=0, row=0, sticky="nsew")

        # Symbol Table 
        symbol_table_frame =  ctk.CTkFrame(upper_right_frame)
        symbol_table_frame.grid(column=0, row=1, sticky="nsew")
        symbol_table_frame.grid_columnconfigure(0, weight=1)
        symbol_table_frame.grid_rowconfigure(0, weight=1)

        self.symbol_table = ttk.Treeview(symbol_table_frame, columns=("Identifier", "Value"), show="headings")
        self.symbol_table.grid(column=0, row=0, sticky="new")
        self.symbol_table.column("#1", anchor=ctk.CENTER)
        self.symbol_table.heading("#1", text="Identifier")
        self.symbol_table.column("#2", anchor=ctk.CENTER)
        self.symbol_table.heading("#2", text="Value")

        symbol_table_scrollbar = ttk.Scrollbar(symbol_table_frame, orient="vertical", command=self.symbol_table.yview)
        self.symbol_table.configure(yscroll=symbol_table_scrollbar.set)
        symbol_table_scrollbar.grid(column=1, row=0, sticky="ns")

        execute_frame = ctk.CTkFrame(self)
        execute_frame.grid(column=0, row=1, columnspan=3, sticky="ew", padx=5, pady=5)
        execute_frame.columnconfigure(0, weight=1)

        execute_button = ctk.CTkButton(execute_frame, text="EXECUTE", command=self.execute, border_spacing=0, height=7)
        execute_button.grid(column=0, row=0, sticky="nsew", pady=0)

        console_frame = ctk.CTkFrame(self, fg_color='green')
        console_frame.grid(column=0, row=2, columnspan=3, sticky="nsew")
        console_frame.grid_columnconfigure(0, weight=1)
        console_frame.grid_rowconfigure(0, weight=1)

        self.console = ctk.CTkTextbox(console_frame)
        self.console.grid(column=0, row=0, sticky="nsew")

    def select_file(self) -> None:
        # Clear text editor
        self.text_editor.delete("0.0", "end")

        selected_file = ctk.filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=(("LOLCODE files", "*.lol*"), ("all files", "*.*")))
        if selected_file:
            self.current_filepath = selected_file
            self.current_filename.set(os.path.basename(selected_file))
        else:
            self.current_filepath = None
            self.current_filename.set('(None)')
            return

        file = open(self.current_filepath, 'r')
        self.lolcode_source = file.read()
        file.close()

        self.text_editor.insert(ctk.END, self.lolcode_source)

    def execute(self) -> None:
        # Reset tokens & token table
        self.tokens = []
        for token in self.token_table.get_children():
            self.token_table.delete(token)

        # save edits
        self.lolcode_source = self.text_editor.get("1.0", "end-1c")
        file = open(self.current_filepath, 'w')
        file.write(self.lolcode_source)
        file.close()
        
        la.lexical_analysis(self.tokens, self.lolcode_source)

        print(self.tokens)

        # insert tokens to the token table
        deduped_tokens = self.tokens
        # deduped_tokens = list(dict.fromkeys(self.tokens))     # TODO UNCOMMENT
        for token in deduped_tokens:
            self.token_table.insert("", 'end', text="1", values=token)

if __name__=="__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    app = LolcodeInterpreterApp()
    app.mainloop()