# ----------------------------------------------------------------------------
# -                        Open3D: www.open3d.org                            -
# ----------------------------------------------------------------------------
# Copyright (c) 2018-2023 www.open3d.org
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------

import open3d as o3d
from open3d.visualization import gui, rendering
import pymeshlab
import os

class AppWindow:
    button_start_text = {
        "stream": "Start streaming camera view",
        "export": "Export ply scan",
        "measure": "Measure distance",
        "show_scan": "Show ply scan",
        "calibrate": "Calibrate camera",
        "start_scan": "Start scan"
    }
    button_stop_text = {
        "stream": "Stop streaming camera view",
        "export": "Export ply scan",
        "measure": "Stop measuring",
        "show_scan": "Hide ply scan",
        "calibrate": "Calibrate camera",
        "start_scan": "Finish scan"
    }

    def __init__(self, width, height):
        self.buttons = dict()
        self.button_is_clicked_mapper = dict()

        gui.Application.instance.initialize()
        self._set_scene(width, height)

    def create_button_to_bar(self, name, function):
        button = gui.Button(name)

        button.horizontal_padding_em = 0.5
        button.vertical_padding_em = 0.5
        button.set_on_clicked(function)
        button.text = self.button_start_text[name]

        self._settings_panel.add_child(button)
        self.buttons[name] = button
        self.button_is_clicked_mapper[name] = False

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

        self._settings_panel = gui.Vert(
            0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))

        self.create_button_to_bar("stream", function=self.start_stream)
        self.create_button_to_bar("start_scan", function=self.start_scan)

        self.create_button_to_bar("show_scan", function=self.show_ply_scene)
        self.create_button_to_bar("measure", function=self.measure_distances_in_ply_scene)


        self.create_button_to_bar("export", function=self.export_file)
        self.create_button_to_bar("calibrate", function=self.calibrate_camera)

        self.buttons["start_scan"].visible = False

        w.set_on_layout(self._on_layout)
        w.add_child(self._scene)
        w.add_child(self._settings_panel)

    def update_button_click_state(self, button_id):
        is_clicked = self.button_is_clicked_mapper[button_id]
        updated_is_clicked = not is_clicked
        self.button_is_clicked_mapper[button_id] = updated_is_clicked

    def update_ply_scan_view(self, button_id):
        button_clicked = self.button_is_clicked_mapper[button_id]

        geometry_name = "pcd"
        scene = self._scene.scene
        pcd_path = "dataset/realsense/scene/integrated.ply"  # todo get self.ply_file from streaming and stitching the file
        pcd = o3d.io.read_point_cloud(pcd_path)

        material = rendering.MaterialRecord()
        material.point_size = 5.0

        if button_clicked:
            scene.add_geometry(geometry_name, pcd, material)
        else:
            scene.remove_geometry(geometry_name)

    def change_button_text(self, button_id):
        button = self.buttons[button_id]
        is_clicked = self.button_is_clicked_mapper[button_id]
        button_text = self.button_stop_text[button_id] if is_clicked else self.button_start_text[button_id]
        button.text = button_text

    def start_stream(self):
        print("Starting stream...")
        BUTTON_ID = "stream"

        self.update_button_click_state(BUTTON_ID)
        self.change_button_text(BUTTON_ID)

        button_clicked = self.button_is_clicked_mapper[BUTTON_ID]

        self.buttons["start_scan"].visible = button_clicked
        self.buttons["show_scan"].visible = not button_clicked

        self.window.set_on_layout(self._on_layout)
        self.window.add_child(self._settings_panel)

    def export_file(self):
        print("Exporting ply file...")
        BUTTON_ID = "export"
        self.location = os.getcwd()
        self.update_button_click_state(BUTTON_ID)
        self.change_button_text(BUTTON_ID)

        dlg = gui.FileDialog(gui.FileDialog.SAVE, "Choose file to save",
                             self.window.theme)
        
        login = os.getlogin()
        desktop = self.location.split(login,1)[0]+login+"\Desktop"
        print(self.location)
        print(desktop)
        
        dlg.set_path(desktop)
        dlg.add_filter(".ply", "Polygon files (.ply)")
        dlg.add_filter(".stl", "Stereolithography files (.stl)")
        dlg.add_filter(".obj", "Wavefront OBJ files (.obj)")
        dlg.set_on_cancel(self._on_file_dialog_cancel)
        dlg.set_on_done(self._on_export_dialog_done)

        self.window.show_dialog(dlg)
    
    def _on_export_dialog_done(self, filename):
        os.chdir(self.location)
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh("dataset/realsense/scene/integrated.ply")
        ms.save_current_mesh(filename)

        self.window.close_dialog()
        
    
    def _on_file_dialog_cancel(self):
        self.window.close_dialog()
    

    def measure_distances_in_ply_scene(self):
        print("Starting measure distance...")
        BUTTON_ID = "measure"

        self.update_button_click_state(BUTTON_ID)
        self.change_button_text(BUTTON_ID)
        pass  #todo

    def show_ply_scene(self):
        BUTTON_ID = "show_scan"

        self.update_button_click_state(BUTTON_ID)
        self.change_button_text(BUTTON_ID)

        button_clicked = self.button_is_clicked_mapper[BUTTON_ID]

        self.buttons["stream"].visible = not button_clicked

        self.window.set_on_layout(self._on_layout)
        self.window.add_child(self._settings_panel)

        self.update_ply_scan_view(BUTTON_ID)

    def calibrate_camera(self):
        print("Calibrating camera...")
        BUTTON_ID = "calibrate"

        self.update_button_click_state(BUTTON_ID)
        self.change_button_text(BUTTON_ID)
        pass #todo

    def start_scan(self):
        from sensors.realsense_recorder import scan
        from src.run_system import get_pointcloud

        print("Starting scanning...")
        BUTTON_ID = "start_scan"

        

        self.update_button_click_state(BUTTON_ID)
        self.change_button_text(BUTTON_ID)

        gui.Application.instance.post_to_main_thread(self.window, scan)
        
        #gui.Application.instance.post_to_main_thread(
        #            self.window, get_pointcloud)

        #get_pointcloud()

        pass #todo

    def _on_layout(self, layout_context):
        r = self.window.content_rect
        self._scene.frame = r
        width = 17 * layout_context.theme.font_size
        height = self.height
        self._settings_panel.frame = gui.Rect(r.get_left(), r.y, width,
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
