from dataclasses import dataclass
from .handler import EventHandler
from .style import colors
import tkinter as tk
from . import DEFAULTS


@dataclass
class UserSetting:
    key: str
    var: tk.IntVar
    label: tk.Label
    entry: tk.Entry = None


@dataclass
class Interface:
    """Responsible for constructing and binding the UI widgets that get user input"""

    handler: EventHandler

    # Entries on Left Button Frame ============================================
    def make_left_frame_entries(self, parent: tk.Frame) -> None:
        # Creates user settings object from defaults
        user_settings: list[UserSetting] = [
            UserSetting(
                key,
                tk.IntVar(value=value),
                tk.Label(
                    parent,
                    text=(
                        key.title()
                        if key not in ["cols", "rows"]
                        else f"# {key.title()}"
                    ),
                    bg=colors.ROOT_BG,
                    justify=tk.LEFT,
                    padx=20,
                ),
            )
            for key, value in DEFAULTS.items()
        ]

        # Creates entries with vars attached
        for setting in user_settings:
            setting.entry = tk.Entry(
                parent,
                textvariable=setting.var,
                width=8,
                justify=tk.CENTER,
                foreground=colors.TEXT,
                bd=0,
                relief="flat",
                bg=colors.ENTRY_BG,
                highlightthickness=1,
                highlightbackground=colors.CANVAS_BG,
                highlightcolor=colors.CANVAS_BG,
                disabledbackground=colors.CANVAS_BLOCK,
            )

        self.user_settings = {setting.key: setting for setting in user_settings}

    def bind_left_frame_entries(self) -> None:
        def call(key, value):
            return lambda e: self.handler.on_change_setting(key, value)

        # Binds entries to set_property method.
        for setting in self.user_settings.values():
            this_call = call(setting.key, setting.var)

            setting.entry.bind("<Return>", this_call)
            setting.entry.bind("<FocusOut>", this_call)
            setting.entry.bind("<KP_Enter>", this_call)

    def grid_entries(self, parent: tk.Frame):
        i = 1
        for setting in self.user_settings.values():
            setting.label.grid(column=3, row=i, padx=0, pady=10, sticky=tk.W)
            setting.entry.grid(column=4, row=i, padx=10, ipady=5)

            if setting.key in ("height", "gutter"):
                i += 1

                # Adds spacer.
                tk.Label(parent, height=1, background=colors.ROOT_BG).grid(
                    column=2, row=i, pady=3
                )
            i += 1

    # Button to link margins ==================================================
    def make_link_margins_button(self, parent: tk.Frame):
        link_margins = tk.Label(parent, text="🔗", foreground=colors.TEXT_DARKER)
        link_margins.bind("<Button-1>", self.on_link_margins, add="+")
        link_margins.grid(column=2, row=5, rowspan=2, sticky=tk.W, padx=4)
        self.link_margins_button = link_margins

    def on_link_margins(
        self, event: tk.Event
    ) -> None:  # Still problematic because a change in top entry won't update the rest now.
        """Transforms Top Entry into a control for all margins at once, disables other margin controls"""

        top, left = self.user_settings["top"], self.user_settings["left"]
        bottom, right = self.user_settings["bottom"], self.user_settings["right"]

        # Calls the event for the first time to update all margins, then binds the entry.

        call = lambda e: self.handler.on_change_setting(key="margin", var=top.var)

        top.label.configure(text="Margin")

        # Unbinds margin top entry.
        top.entry.unbind("<Return>")
        top.entry.unbind("<FocusOut>")
        top.entry.unbind("<KP_Enter>")

        # Rebinds it to change everything.
        top.entry.bind("<Return>", call)
        top.entry.bind("<FocusOut>", call)
        top.entry.bind("<KP_Enter>", call)

        top.entry.bind("<Return>", self.sync_vars_to_top, add="+")
        top.entry.bind("<FocusOut>", self.sync_vars_to_top, add="+")
        top.entry.bind("<KP_Enter>", self.sync_vars_to_top, add="+")

        # Disables left, bottom and right margin Entries and darkens Label text.
        lbr_labels = [_.label for _ in (left, bottom, right)]
        lbr_entries = [_.entry for _ in (left, bottom, right)]

        self.sync_vars_to_top()
        for entry, label in zip(lbr_entries, lbr_labels):
            entry.configure(state="disabled")
            label.configure(foreground=colors.TEXT_DARKER)

        # Bind for unlinking now.
        link_margins_button: tk.Label = event.widget
        link_margins_button.unbind("<Button-1>")
        link_margins_button.bind("<Button-1>", self.on_unlink_margins)

        self.handler.on_change_setting(key="margin", var=top.var)

    def on_unlink_margins(self, event: tk.Event):
        # Enables left, bottom and right margin Entries and lightens Label text.
        top, left = self.user_settings["top"], self.user_settings["left"]
        bottom, right = self.user_settings["bottom"], self.user_settings["right"]

        lbr_labels = [_.label for _ in (left, bottom, right)]
        lbr_entries = [_.entry for _ in (left, bottom, right)]

        for entry, label in zip(lbr_entries, lbr_labels):
            entry.configure(state=tk.NORMAL)
            label.configure(foreground=colors.TEXT)

        # rebind link button
        link_margins_button: tk.Label = event.widget
        link_margins_button.unbind("<Button-1>")
        link_margins_button.bind("<Button-1>", self.on_link_margins)

        # Rebind Top Entry to only change Top
        call = lambda e: self.handler.on_change_setting(key="top", var=top.var)

        top.label.configure(text="Top")

        top.entry.unbind("<Return>")
        top.entry.unbind("<FocusOut>")
        top.entry.unbind("<KP_Enter>")

        top.entry.bind("<Return>", call)
        top.entry.bind("<FocusOut>", call)
        top.entry.bind("<KP_Enter>", call)

    def sync_vars_to_top(self, event: tk.Event = None):
        top_value = self.user_settings["top"].var.get()
        vars = [
            setting.var
            for setting in self.user_settings.values()
            if setting.key in ["left", "bottom", "right"]
        ]
        for var in vars:
            var.set(top_value)

    # Transformation buttons ==================================================
    def make_transformation_buttons(self):
        raise NotImplementedError()

    def bind_transformation_buttons(self):
        raise NotImplementedError()
