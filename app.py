import tkinter as tk
from .style import colors, fonts
from .core import Canvas, Margin, Grid
from . import (
    DEFAULTS,
    ResolveFusionAPI,
    ScreenSplitterGUI,
    Controller,
    EventHandler,
    UserInput,
)


class App:
    def build_layout(self):
        self.root = tk.Tk()
        root = self.root

        # Configures root.  ===================================================
        # Window config
        root.attributes("-topmost", True)
        root.resizable(False, False)
        root.title("SplitScreener")

        # Bg config
        root.configure(bg=colors.ROOT_BG)
        root.option_add("*background", colors.ROOT_BG)

        # Text config
        root.option_add("*font", fonts.MAIN)
        root.option_add("*foreground", colors.TEXT)

        # Entry config
        root.option_add("*Entry.foreground", colors.TEXT)
        root.option_add("*Entry.background", colors.ENTRY_BG)
        root.option_add("*Entry.disabledbackground", colors.TEXT_DARKER)

        # Sets up the main window grid.  ======================================
        root.columnconfigure(index=1, weight=1, minsize=220)  # LEFT SIDEBAR
        root.columnconfigure(index=2, weight=1, minsize=820)  # MAIN SECTION
        root.columnconfigure(index=3, weight=1, minsize=150)  # RIGHT SIDEBAR
        root.rowconfigure(index=1, weight=3)  # HEADER
        root.rowconfigure(index=2, weight=1)  # MAIN SECTION
        root.rowconfigure(index=3, weight=1)  # THE RENDER BUTTON (deprecated)
        root.rowconfigure(index=4, weight=3)  # FOOTER

        # Creates and places frames for UI Widgets ============================
        self.header = tk.Frame(root)
        self.frame_left_entries = tk.Frame(root)
        self.frame_screen_creation = tk.Frame(root)
        self.frame_right_transformations = tk.Frame(root)
        self.footer = tk.Frame(root)

        # Adding to grid...
        self.header.grid(column=1, row=1, columnspan=3)
        self.frame_left_entries.grid(column=1, row=2)
        self.frame_screen_creation.grid(column=2, row=2, padx=10, pady=10)
        self.frame_right_transformations.grid(column=3, row=2, ipadx=20)
        self.footer.grid(column=1, row=3, columnspan=3)

    def initialize_splitscreener(self):
        canvas = Canvas((DEFAULTS["width"], DEFAULTS["height"]))
        margin = Margin(
            canvas,
            tlbr=tuple(
                DEFAULTS[key]
                for key in DEFAULTS
                if key in ("top", "left", "bottom", "right")
            ),
            gutter=DEFAULTS["gutter"],
        )
        self.grid = Grid(canvas, margin)

    def initialize_user_interface(self):
        # Resolve API
        self.api = ResolveFusionAPI()
        self.api.add_canvas(*self.grid.canvas.resolution)

        # Screen Creation UI
        self.gui = ScreenSplitterGUI(
            master=self.frame_screen_creation,
            ss_grid=self.grid,
            max_width=800,
            max_height=600,
        )
        self.gui.draw_canvas()
        self.gui.grid(row=1)
        self.gui.draw_grid()

        # Controller
        self.controller = Controller(self.grid, self.api, self.gui)

        # Handler
        self.handler = EventHandler(self.controller, self.gui)

        # Interface – Left Frame
        self.interface = UserInput(self.handler)
        self.interface.make_left_frame_entries(self.frame_left_entries)
        self.interface.bind_left_frame_entries()
        self.interface.grid_entries(self.frame_left_entries)
        self.interface.make_link_margins_button(self.frame_left_entries)

        # Interface – Transformation buttons
        frame = self.frame_right_transformations

        frame.columnconfigure(index=1, weight=1)
        for i in range(6):
            frame.rowconfigure(index=i + 1, weight=1)
        frame.option_add("*font", fonts.SMALL)

        self.interface.make_transformation_buttons(frame)

    def run(self):
        try:
            self.root.mainloop()
        except NameError:
            raise Exception("Please initialize a root tk window first.")
