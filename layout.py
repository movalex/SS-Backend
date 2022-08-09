import tkinter as tk
from .style import colors, fonts


class AppLayout:
    def make_layout(self):
        self.root = tk.Tk()
        root = self.root

        # ROOT CONFIGS =========================================================
        root.configure(bg=colors.ROOT_BG)
        root.option_add("*font", fonts.MAIN)
        root.option_add("*foreground", colors.TEXT)
        root.option_add("*Entry.foreground", colors.TEXT)
        root.option_add("*Entry.background", colors.ENTRY_BG)
        root.option_add("*Entry.disabledbackground", colors.TEXT_DARKER)
        root.option_add("*background", colors.ROOT_BG)
        root.option_add("*Checkbutton.font", fonts.SMALL)
        root.attributes("-topmost", True)
        # root.minsize(1260, 740)
        root.title("SplitScreener 1.0")
        root.resizable(False, False)

        # SETTING UP THE MAIN TK GRID ======================================================
        root.columnconfigure(index=1, weight=1, minsize=220)  # LEFT SIDEBAR
        root.columnconfigure(
            index=2, weight=1, minsize=820
        )  # MAIN SECTION, THE CREATOR
        root.columnconfigure(
            index=3, weight=1, minsize=150
        )  # RIGHT SIDEBAR (nothing there yet)
        root.rowconfigure(index=1, weight=3)  # HEADER
        root.rowconfigure(
            index=2, weight=1
        )  # MAIN SECTION, THE CREATOR FRAME AND SETTINGS
        root.rowconfigure(index=3, weight=1)  # THE RENDER BUTTON FRAME
        root.rowconfigure(index=4, weight=3)  # FOOTER

        # CREATING THE FRAMES
        self.header = tk.Frame(root)
        self.button_frame_left = tk.Frame(root)
        self.creator_frame = tk.Frame(root)
        self.button_frame_right = tk.Frame(root)
        self.footer = tk.Frame(root)

        # adding them to the grid
        self.header.grid(column=1, row=1, columnspan=3)
        self.button_frame_left.grid(column=1, row=2)
        self.creator_frame.grid(column=2, row=2, padx=10, pady=10)
        self.button_frame_right.grid(column=3, row=2, ipadx=20)
        self.footer.grid(column=1, row=3, columnspan=3)
