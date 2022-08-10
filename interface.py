from dataclasses import dataclass
from .handler import EventHandler
from .style import colors
import tkinter as tk


@dataclass
class Interface:
    """Responsible for constructing and binding the UI widgets that get user input"""

    handler: EventHandler

    # Entries on Left Button Frame ============================================
    def make_left_frame_entries(
        self, defaults: dict[str, int], parent: tk.Frame
    ) -> None:
        # creates dict with vars and labels
        user_settings: dict[str, list[tk.IntVar | tk.Label | tk.Entry]] = {
            key: [
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
            ]
            for key, value in defaults.items()
        }

        # creates entries with vars attached
        for value in user_settings.values():
            value.append(
                tk.Entry(
                    parent,
                    textvariable=value[0],
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
            )

        self.user_settings = user_settings

    def bind_left_frame_entries(self) -> None:
        def call(key, value):
            return lambda e: self.handler.on_change_setting(key, value)

        # Binds entries to set_property method.
        for key, value in self.user_settings.items():
            var: tk.IntVar = value[0]
            entry: tk.Entry = value[2]

            this_call = call(key, var)

            entry.bind("<Return>", this_call)
            entry.bind("<FocusOut>", this_call)
            entry.bind("<KP_Enter>", this_call)

    def grid_entries(self, parent: tk.Frame):
        i = 1
        for key, group in self.user_settings.items():
            label, entry = group[1], group[2]
            label.grid(column=3, row=i, padx=0, pady=10, sticky=tk.W)
            entry.grid(column=4, row=i, padx=10, ipady=5)
            if key in ("height", "gutter"):
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

        top_var, top_label, top_entry = self.user_settings["top"]

        # Calls the event for the first time to update all margins, then binds the entry.

        call = lambda e: self.handler.on_change_setting(key="margin", var=top_var)

        top_label.configure(text="Margin")

        # Unbinds margin top entry.
        top_entry.unbind("<Return>")
        top_entry.unbind("<FocusOut>")
        top_entry.unbind("<KP_Enter>")

        # Rebinds it to change everything.
        top_entry.bind("<Return>", call)
        top_entry.bind("<FocusOut>", call)
        top_entry.bind("<KP_Enter>", call)

        top_entry.bind("<Return>", self.sync_vars_to_top, add="+")
        top_entry.bind("<FocusOut>", self.sync_vars_to_top, add="+")
        top_entry.bind("<KP_Enter>", self.sync_vars_to_top, add="+")

        # Disables left, bottom and right margin Entries and darkens Label text.
        lbr_vars: dict[str, tk.IntVar] = {
            key: self.user_settings[key][0] for key in ("left", "bottom", "right")
        }
        lbr_labels: dict[str, tk.Label] = {
            key: self.user_settings[key][1] for key in ("left", "bottom", "right")
        }
        lbr_entries: dict[str, tk.Entry] = {
            key: self.user_settings[key][2] for key in ("left", "bottom", "right")
        }

        self.sync_vars_to_top()
        for entry, label in zip(lbr_entries.values(), lbr_labels.values()):
            entry.configure(state="disabled")
            label.configure(foreground=colors.TEXT_DARKER)

        # Bind for unlinking now.
        link_margins_button: tk.Label = event.widget
        link_margins_button.unbind("<Button-1>")
        link_margins_button.bind("<Button-1>", self.on_unlink_margins)

        self.handler.on_change_setting(key="margin", var=top_var)

    def on_unlink_margins(self, event: tk.Event):
        # Enables left, bottom and right margin Entries and lightens Label text.
        lbr_labels: dict[str, tk.Label] = {
            key: self.user_settings[key][1] for key in ("left", "bottom", "right")
        }
        lbr_entries: dict[str, tk.Entry] = {
            key: self.user_settings[key][2] for key in ("left", "bottom", "right")
        }

        for entry, label in zip(lbr_entries.values(), lbr_labels.values()):
            entry.configure(state=tk.NORMAL)
            label.configure(foreground=colors.TEXT)

        # rebind link button
        link_margins_button: tk.Label = event.widget
        link_margins_button.unbind("<Button-1>")
        link_margins_button.bind("<Button-1>", self.on_link_margins)

        # Rebind Top Entry to only change Top
        top_var, top_label, top_entry = self.user_settings["top"]
        call = lambda e: self.handler.on_change_setting(key="top", var=top_var)

        top_label.configure(text="Top")

        top_entry.unbind("<Return>")
        top_entry.unbind("<FocusOut>")
        top_entry.unbind("<KP_Enter>")

        top_entry.bind("<Return>", call)
        top_entry.bind("<FocusOut>", call)
        top_entry.bind("<KP_Enter>", call)

    def sync_vars_to_top(self, event: tk.Event = None):
        top = self.user_settings["top"][0].get()
        vars = [
            self.user_settings[key][0]
            for key in self.user_settings
            if key in ("left", "bottom", "right")
        ]
        for var in vars:
            var.set(top)

    # Transformation buttons ==================================================
    def make_transformation_buttons(self):
        raise NotImplementedError()

    def bind_transformation_buttons(self):
        raise NotImplementedError()
