# ----------------------------------------------------------------------------
# -                        Open3D: www.open3d.org                            -
# ----------------------------------------------------------------------------
# Copyright (c) 2018-2023 www.open3d.org
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------
import numpy as np
import open3d as o3d
from open3d.visualization import gui, rendering
from sensors.realsense_recorder import scan
from src.run_system import get_pointcloud


BUTTON_START_STREAM_ID = "start_stream"
BUTTON_STOP_STREAM_ID = "stop_stream"
BUTTON_START_SCAN_ID = "start_scan"
BUTTON_EXPORT_ID = "export"
BUTTON_START_MEASURE_ID = "start_measure"
BUTTON_STOP_MEASURE_ID = "stop_measure"
BUTTON_SHOW_SCAN_ID = "show_scan"
BUTTON_HIDE_SCAN_ID = "hide_scan"
BUTTON_CALIBRATE_ID = "calibrate"

MAIN_SCREEN_ID = "main_screen"


class AppWindow:
    button_text_mapper = {
        BUTTON_START_STREAM_ID: "START STREAM",
        BUTTON_STOP_STREAM_ID: "STOP STREAM",
        BUTTON_START_SCAN_ID: "START SCAN",
        BUTTON_EXPORT_ID: "EXPORT TO PLY",
        BUTTON_START_MEASURE_ID: "START MEASURING",
        BUTTON_STOP_MEASURE_ID: "STOP MEASURING",
        BUTTON_SHOW_SCAN_ID: "SHOW SCAN",
        BUTTON_HIDE_SCAN_ID: "HIDE SCAN",
        BUTTON_CALIBRATE_ID: "CALIBRATE",
    }

    def __init__(self, width, height):
        self.pcd = None
        self.buttons = dict()
        self.button_is_clicked_mapper = dict()

        gui.Application.instance.initialize()
        self._set_scene(width, height)

    def create_button_to_bar(self, name, function, visibility=True):
        button = gui.Button(name)

        button.horizontal_padding_em = 0.5
        button.vertical_padding_em = 0.5
        button.set_on_clicked(function)

        button.text = self.button_text_mapper[name]
        button.visible = visibility

        self._left_panel.add_child(button)
        self.buttons[name] = button
        self.button_is_clicked_mapper[name] = False

    def update_visiblity(self, button_to_visibility_mapper: dict[str, bool]):
        for button_id in button_to_visibility_mapper.keys():
            self.buttons[button_id].visible = button_to_visibility_mapper[button_id]
        self.window.set_on_layout(self._on_layout)
        self.window.add_child(self._left_panel)

    def _set_scene(self, width, height):
        self.window = gui.Application.instance.create_window(
            "Realsense APP (FMFI UK project)", width, height)
        w = self.window
        self.width = width
        self.height = height

        # 3D widget
        self._scene = gui.SceneWidget()
        self._scene.scene = rendering.Open3DScene(w.renderer)

        em = w.theme.font_size

        self._left_panel = gui.Vert(
            0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))

        self.create_button_to_bar(BUTTON_START_STREAM_ID, function=self.start_stream)
        self.create_button_to_bar(BUTTON_STOP_STREAM_ID, function=self.stop_stream, visibility=False)

        self.create_button_to_bar(BUTTON_START_SCAN_ID, function=self.start_scan)

        self.create_button_to_bar(BUTTON_SHOW_SCAN_ID, function=self.show_ply_scene)
        self.create_button_to_bar(BUTTON_HIDE_SCAN_ID, function=self.hide_scan, visibility=False)

        self.create_button_to_bar(BUTTON_START_MEASURE_ID, function=self.start_measure)
        self.create_button_to_bar(BUTTON_STOP_MEASURE_ID, function=self.stop_measure, visibility=False)

        self.create_button_to_bar(BUTTON_EXPORT_ID, function=self.export_file)
        self.create_button_to_bar(BUTTON_CALIBRATE_ID, function=self.calibrate_camera)

        w.set_on_layout(self._on_layout)
        w.add_child(self._scene)
        w.add_child(self._left_panel)

    def start_stream(self):
        visibility_after_click_mapper = {
            BUTTON_START_STREAM_ID: False,
            BUTTON_STOP_STREAM_ID: True,
            BUTTON_START_SCAN_ID: True,
            BUTTON_EXPORT_ID: False,
            BUTTON_START_MEASURE_ID: False,
            BUTTON_STOP_MEASURE_ID: False,
            BUTTON_SHOW_SCAN_ID: False,
            BUTTON_HIDE_SCAN_ID: False,
            BUTTON_CALIBRATE_ID: False,
        }
        self.update_visiblity(visibility_after_click_mapper)
        pass  # todo

    def stop_stream(self):
        visibility_after_click_mapper = {
            BUTTON_START_STREAM_ID: True,
            BUTTON_STOP_STREAM_ID: False,
            BUTTON_START_SCAN_ID: True,
            BUTTON_EXPORT_ID: True,
            BUTTON_START_MEASURE_ID: True,
            BUTTON_STOP_MEASURE_ID: False,
            BUTTON_SHOW_SCAN_ID: True,
            BUTTON_HIDE_SCAN_ID: False,
            BUTTON_CALIBRATE_ID: True,
        }
        self.update_visiblity(visibility_after_click_mapper)
        pass  # todo

    def start_scan(self):
        gui.Application.instance.post_to_main_thread(self.window, scan)
        
        #gui.Application.instance.post_to_main_thread(
        #            self.window, get_pointcloud)

        self.pcd = get_pointcloud()  #todo ak get_pointcloud vracia pcd, tak by som to dal do self.pcd a pracoval neskor s tymito datami


    def show_ply_scene(self):
        if not self.pcd:
            print("No PLY file defined.")
            return

        visibility_after_click_mapper = {
            BUTTON_START_STREAM_ID: False,
            BUTTON_STOP_STREAM_ID: False,
            BUTTON_START_SCAN_ID: False,
            BUTTON_EXPORT_ID: False,
            BUTTON_START_MEASURE_ID: True,
            BUTTON_STOP_MEASURE_ID: False,
            BUTTON_SHOW_SCAN_ID: False,
            BUTTON_HIDE_SCAN_ID: True,
            BUTTON_CALIBRATE_ID: False,
        }
        self.update_visiblity(visibility_after_click_mapper)

        scene = self._scene.scene

        material = rendering.MaterialRecord()
        material.shader = "defaultUnlit"
        material.point_size = 5.0

        scene.add_geometry(MAIN_SCREEN_ID, self.pcd, material)

    def hide_scan(self):
        visibility_after_click_mapper = {
            BUTTON_START_STREAM_ID: True,
            BUTTON_STOP_STREAM_ID: False,
            BUTTON_START_SCAN_ID: True,
            BUTTON_EXPORT_ID: True,
            BUTTON_START_MEASURE_ID: False,
            BUTTON_STOP_MEASURE_ID: False,
            BUTTON_SHOW_SCAN_ID: True,
            BUTTON_HIDE_SCAN_ID: False,
            BUTTON_CALIBRATE_ID: True,
        }
        self.update_visiblity(visibility_after_click_mapper)

        scene = self._scene.scene
        scene.remove_geometry(MAIN_SCREEN_ID)

    def export_file(self):
        pass  # todo

    def start_measure(self):
        if not self.pcd:
            print("No PLY file defined.")
            return

        visibility_after_click_mapper = {
            BUTTON_START_MEASURE_ID: False,
            BUTTON_STOP_MEASURE_ID: True,
        }
        self.update_visiblity(visibility_after_click_mapper)


        def pick_points(pcd):
            print("1) Shift + Left Click to select points.")
            print("2) Press 'Q' to finish and close the window.")

            vis = o3d.visualization.VisualizerWithEditing()
            vis.create_window()
            vis.add_geometry(pcd)
            vis.run()
            vis.close()

            return vis.get_picked_points()

        picked_indices = pick_points(self.pcd)

        if len(picked_indices) >= 2:
            print("Picked points indices:", picked_indices)
            point1 = np.asarray(self.pcd.points)[picked_indices[0]]
            point2 = np.asarray(self.pcd.points)[picked_indices[1]]

            # Calculate the Euclidean distance
            distance = np.linalg.norm(point1 - point2)
            print(f"Distance between points: {distance}")
        else:
            print(f"Expected at least 2 points, but picked {len(picked_indices)}. Please try again.")

        self.run()

    def stop_measure(self):
        visibility_after_click_mapper = {
            BUTTON_START_MEASURE_ID: True,
            BUTTON_STOP_MEASURE_ID: False,
        }
        self.update_visiblity(visibility_after_click_mapper)

        pass  # todo

    def calibrate_camera(self):
        pass  #todo kalibracia asi nebude potrebna

    def _on_layout(self, layout_context):
        r = self.window.content_rect
        self._scene.frame = r
        width = 17 * layout_context.theme.font_size
        height = self.height
        self._left_panel.frame = gui.Rect(r.get_left(), r.y, width,
                                          height)

    @staticmethod
    def run():
        gui.Application.instance.run()


def main():
    # We need to initialize the application, which finds the necessary shaders
    # for rendering and prepares the cross-platform window abstraction.

    w = AppWindow(2048, 768)
    w.run()


if __name__ == "__main__":
    main()
