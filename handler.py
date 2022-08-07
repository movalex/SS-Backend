from dataclasses import dataclass
import tkinter as tk
from .style import colors
from .controller import Controller


@dataclass
class UIHandler:
    """Responsible for getting input from user interaction and passing it along to the Controller."""

    controller: Controller

    def change_setting(self, event: tk.Event, **kwargs: dict[str, function]) -> None:
        key_to_pass_along = kwargs.keys()[0]
        value_to_pass_along = kwargs.values()[0]()

        self.controller.user_request(key_to_pass_along, value_to_pass_along)

    def request_new_screen():
        ...


def make_entries(defaults: dict[str, int], ui_handler: UIHandler):
    # creates dict with vars and labels
    user_settings = {
        key: [tk.IntVar(value=value), tk.Label(text=key.title())]
        for key, value in defaults.items()
    }

    # creates entries with vars attached
    for value in user_settings.values():
        value.append(tk.Entry(textvariable=value[0]))

    # binds entries to set_property method
    for key, value in user_settings.items():
        var: tk.IntVar = value[0]
        entry: tk.Entry = value[2]

        call = lambda self, event: ui_handler.change_setting(**{key: var.get})

        entry.bind("<Return>", call)
        entry.bind("<FocusOut>", call)
        entry.bind("<KP_Enter>", call)


# this is how it should look: {"width": [tk.IntVar(), tk.Label(), tk.Entry()]}


# LINK MARGINS ======================================================================

# link button

link_margins = tk.Label(button_frame_left, text="🔗", foreground=colors.TEXT_DARKER)
link_margins.grid(column=2, row=5, rowspan=2, sticky=tk.W, padx=4)
set_hover_style(link_margins)
link_margins.bind("<Button-1>", screen_splitter.link_margins, add="+")


# ENTRIES FOR USER INPUT ==============================================
def mk_entries(parent: tk.Frame, vars: dict[str, tk.IntVar]):
    var_entries = {}
    for key, var in vars.items():
        new_key = key
        if key == "cols" or key == "rows":
            new_key = f"# {key}"
        label = tk.Label(
            parent, text=new_key.title(), bg=colors.ROOT_BG, justify=tk.LEFT, padx=20
        )

        entry = tk.Entry(
            parent,
            width=8,
            justify=tk.CENTER,
            textvariable=var,
            foreground=colors.TEXT,
            bd=0,
            relief="flat",
            bg=colors.ENTRY_BG,
            highlightthickness=1,
            highlightbackground=colors.CANVAS_BG,
            highlightcolor=colors.CANVAS_BG,
            disabledbackground=colors.CANVAS_BLOCK,
        )
        var_entries[key] = (label, entry)
    return var_entries


def grid_entries(entries: dict[str, tuple[tk.Label, tk.Entry]]):
    i = 1
    for key, tuple in entries.items():
        tuple[0].grid(column=3, row=i, padx=0, pady=10, sticky=tk.W)
        tuple[1].grid(column=4, row=i, padx=10, ipady=5)
        if key == "height" or key == "gutter":
            i += 1
        i += 1

    # adds spacers
    tk.Label(button_frame_left, height=1, background=colors.ROOT_BG).grid(
        column=2, row=3, pady=3
    )
    tk.Label(button_frame_left, height=1, background=colors.ROOT_BG).grid(
        column=2, row=9, pady=3
    )
    tk.Label(button_frame_left, height=1, background=colors.ROOT_BG).grid(
        column=2, row=12, pady=3
    )
