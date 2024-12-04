# ----------------------------------------------------------------------------
# -                        Open3D: www.open3d.org                            -
# ----------------------------------------------------------------------------
# Copyright (c) 2018-2023 www.open3d.org
# SPDX-License-Identifier: MIT
# ----------------------------------------------------------------------------

import os
import sys

import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering


class AppWindow:

    def __init__(self, width, height):
        self.window = gui.Application.instance.create_window(
            "Realsense APP (FMFI UK project)", width, height)
        w = self.window  # to make the code more concise
        self.width = width
        self.height = height

        # 3D widget
        self._scene = gui.SceneWidget()
        self._scene.scene = rendering.Open3DScene(w.renderer)

        em = w.theme.font_size
        separation_height = int(round(0.5 * em))

        self._settings_panel = gui.Vert(
            0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))

        self._start_scan_button = gui.Button("Start scan")
        self._start_scan_button.horizontal_padding_em = 0.5
        self._start_scan_button.vertical_padding_em = 0.5
        self._start_scan_button.set_on_clicked(self.start_stream)  # TODO funkcia na start scan

        self._export_button = gui.Button("Export")
        self._export_button.horizontal_padding_em = 0.5
        self._export_button.vertical_padding_em = 0.5
        self._export_button.set_on_clicked(self._set_mouse_mode_fly)  # TODO funkcia na export

        self._measure_button = gui.Button("Measure")
        self._measure_button.horizontal_padding_em = 0.5
        self._measure_button.vertical_padding_em = 0.5
        self._measure_button.set_on_clicked(self._set_mouse_mode_model)  # TODO funkcia na meranie vzdialenosti

        self._settings_panel.add_fixed(separation_height)
        self._settings_panel.add_child(gui.Label("Menu"))
        self._settings_panel.add_child(self._start_scan_button)
        self._settings_panel.add_child(self._export_button)
        self._settings_panel.add_child(self._measure_button)

        w.set_on_layout(self._on_layout)
        w.add_child(self._scene)
        w.add_child(self._settings_panel)

        # self.mesh = o3d.io.read_triangle_mesh("1.ply")
        # # Add mesh to the scene
        # self._scene.scene.add_geometry("Mesh", self.mesh)

    def _on_layout(self, layout_context):

        r = self.window.content_rect
        self._scene.frame = r
        width = 17 * layout_context.theme.font_size
        height = self.height
        self._settings_panel.frame = gui.Rect(r.get_left(), r.y, width,
                                              height)

    def start_stream(self):
        print("Starting stream...")
        pass

    def _set_mouse_mode_fly(self):
        self._scene.set_view_controls(gui.SceneWidget.Controls.FLY)

    def _set_mouse_mode_model(self):
        self._scene.set_view_controls(gui.SceneWidget.Controls.ROTATE_MODEL)


def main():
    # We need to initialize the application, which finds the necessary shaders
    # for rendering and prepares the cross-platform window abstraction.
    gui.Application.instance.initialize()

    w = AppWindow(2048, 768)

    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.exists(path):
            w.load(path)
        else:
            w.window.show_message_box("Error",
                                      "Could not open file '" + path + "'")

    # Run the event loop. This will not return until the last window is closed.
    gui.Application.instance.run()


if __name__ == "__main__":
    main()
