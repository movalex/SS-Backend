from ss_backend.fusion_alias import Comp, Fusion, Tool
from .utils import find_first_missing

# FAKE FUSION FOR TESTING
def initialize_fake_fusion():

    global fusion, comp
    fusion = Fusion()
    comp = Comp()


try:
    fusion
except NameError:
    initialize_fake_fusion()

# GLOBAL
IS_RESOLVE = True if fusion.GetResolve() else False


class ResolveFusionAPI:
    def __init__(self) -> None:
        self.merges: list[Tool] = []
        self.masks: list[Tool] = []
        self.media_ins: list[Tool] = []
        self.screens: list[set[Tool, Tool, Tool]] = []

    def refresh_global(
        self,
        resolution: tuple[int, int],
        screen_tools: list[tuple[Tool, Tool]] | None = None,
        screen_values: list[dict[str, float]] | None = None,
    ):
        """Calls all necessary methods for when user changes settings."""
        if not (
            self.canvas.GetInput("Width") == resolution[0]
            and self.canvas.GetInput("Height") == resolution[1]
        ):
            self.set_inputs_canvas(*resolution)

        if not screen_tools:
            return

        for tools, values in zip(screen_tools, screen_values):
            merge, mask = tools
            self.set_inputs_screen(merge, mask, **values)

    # POSITIONING NODES ON FLOW
    def refresh_positions(self):
        flow = comp.CurrentFrame.FlowView
        flow.QueueSetPos(self.canvas, 0, 0)
        if self.merges:
            for index, merge in enumerate(self.merges):
                flow.QueueSetPos(merge, 0, index + 1)
            for index, mask in enumerate(self.masks):
                flow.QueueSetPos(mask, 1, index + 1)
            for index, media_in in enumerate(self.media_ins):
                flow.QueueSetPos(media_in, -1, index + 1)
        else:
            index = 0
        flow.QueueSetPos(self.media_out, 0, index + 2)

        flow.FlushSetPosQueue()

    def set_position_media_out(self) -> None:
        flow = comp.CurrentFrame.FlowView
        flow.SetPos(self.media_out, 0, len(self.media_ins) + 1)

    # DEALING WITH REGULAR INPUTS
    def set_inputs(self, tool: Tool, **kwargs) -> None:
        for key, value in kwargs.items():
            tool.SetInput(key, value)

    def set_inputs_batch(self, tools: list[Tool], **kwargs) -> None:
        for tool in tools:
            self.set_inputs(tool, **kwargs)

    def set_inputs_screen(self, merge: Tool, mask: Tool, **kwargs) -> None:
        mask_inps = {key: kwargs[key] for key in ("Width", "Height", "Center")}
        mrg_inps = {key: kwargs[key] for key in ("Center", "Size")}
        self.set_inputs(merge, **mrg_inps)
        self.set_inputs(mask, **mask_inps)

    def set_inputs_canvas(self, width: int, height: int) -> None:
        if self.canvas:
            self.set_inputs(
                self.canvas,
                Width=width,
                Height=height,
            )

    def set_inputs_media_out(self) -> None:
        if self.merges:
            self.media_out.SetInput("Input", self.merges[-1])
        else:
            self.media_out.SetInput("Input", self.canvas)

    # CREATING TOOLS
    def add_canvas(self, width: int, height: int):
        canvas = comp.AddTool("Background", 0, 0)
        canvas.SetAttrs({"TOOLS_Name": "SSCanvas"})
        canvas.SetInput("UseFrameFormatSettings", 0)

        self.canvas = canvas
        self.set_inputs_canvas(width, height)

        self.add_media_out()

    def add_media_out(self):
        media_out = comp.AddTool("MediaOut", 0, 2)
        media_out.SetInput("Input", self.canvas)
        comp.CurrentFrame.ViewOn(media_out, 2)
        self.media_out = media_out

    def add_screen(self, **kwargs) -> tuple[Tool, Tool, Tool]:
        node_y = len(self.merges) + 1

        merge = comp.AddTool("Merge", 0, node_y)
        mask = comp.AddTool("RectangleMask", 1, node_y)
        media_in = comp.AddTool("MediaIn", -1, node_y)

        mask_inps = {key: kwargs[key] for key in ("Width", "Height", "Center")}
        mrg_inps = {key: kwargs[key] for key in ("Center", "Size")}
        media_in.SetInput("Layer", f"{self.next_media_in_layer}")

        mrg_inps["EffectMask"] = mask
        mrg_inps["Foreground"] = media_in
        if self.merges:
            mrg_inps["Background"] = self.merges[-1]
        else:
            mrg_inps["Background"] = self.canvas

        self.set_inputs(merge, **mrg_inps)
        self.set_inputs(mask, **mask_inps)

        self.merges.append(merge)
        self.masks.append(mask)
        self.media_ins.append(media_in)

        self.set_position_media_out()
        self.set_inputs_media_out()

        return merge, mask, media_in

    # DELETING TOOLS
    def delete_tool(self, tool: Tool) -> None:
        tool.Delete()

    def delete_tool_batch(self, *tools: Tool) -> None:
        for tool in tools:
            tool.Delete()

    def delete_screen(self, screen: tuple[Tool, Tool, Tool]) -> None:
        self.delete_tool_batch(*screen)
        self.refresh_positions()

    # UTILS
    @property
    def next_media_in_layer(self):
        if not self.media_ins:
            return 0
        return find_first_missing(
            sorted([int(media_in.GetInput("Layer")) for media_in in self.media_ins])
        )
