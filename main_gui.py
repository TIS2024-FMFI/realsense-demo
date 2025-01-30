import os.path

import numpy as np
import open3d as o3d
import pymeshlab
from open3d.visualization import gui, rendering

APP_NAME = "Realsense APP (FMFI UK project)"

PLY_FILE_PATH = "dataset/realsense/scene/integrated.ply"

SHADER_STYLE = "defaultUnlit"

BUTTON_START_STREAM_ID = "start_stream"
BUTTON_STOP_STREAM_ID = "stop_stream"
BUTTON_START_SCAN_ID = "start_scan"
BUTTON_EXPORT_ID = "export"
BUTTON_START_MEASURE_ID = "start_measure"
BUTTON_STOP_MEASURE_ID = "stop_measure"
BUTTON_SHOW_SCAN_ID = "show_scan"
BUTTON_HIDE_SCAN_ID = "hide_scan"

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
    }

    # FOR MEASUREMENT IN PLY
    _picked_indicates = []
    _picked_positions = []
    _picked_num = 0

    def __init__(self, width, height):
        self.pcd = None
        self.pcd_kdtree = None

        self.buttons = dict()
        self.button_is_clicked_mapper = dict()

        gui.Application.instance.initialize()
        self._set_scene(width, height)

    def _on_layout(self, layout_context):
        r = self.window.content_rect
        self._scene.frame = r
        width = 17 * layout_context.theme.font_size
        height = self.height
        self._left_panel.frame = gui.Rect(r.get_left(), r.y, width,
                                          height)

    def create_button_to_bar(self, name: str, function, visibility=True):
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

    def update_distance(self, distance: float):
        self.distance_text_label.text = f"Distance {str(round(distance, 2))} m"

    def buttons_to_bar(self):
        self.create_button_to_bar(BUTTON_START_STREAM_ID, function=self.start_stream)
        self.create_button_to_bar(BUTTON_STOP_STREAM_ID, function=self.stop_stream, visibility=False)

        self.create_button_to_bar(BUTTON_START_SCAN_ID, function=self.start_scan)

        self.create_button_to_bar(BUTTON_SHOW_SCAN_ID, function=self.show_ply_scene)
        self.create_button_to_bar(BUTTON_HIDE_SCAN_ID, function=self.hide_scan, visibility=False)

        self.create_button_to_bar(BUTTON_START_MEASURE_ID, function=self.start_measure, visibility=False)
        self.create_button_to_bar(BUTTON_STOP_MEASURE_ID, function=self.stop_measure, visibility=False)

        self.create_button_to_bar(BUTTON_EXPORT_ID, function=self.export_file)

    def _set_scene(self, width, height):
        self.window = gui.Application.instance.create_window(APP_NAME, width, height)
        w = self.window
        self.width = width
        self.height = height

        # 3D widget
        self._scene = gui.SceneWidget()
        self._scene.scene = rendering.Open3DScene(w.renderer)

        em = w.theme.font_size
        size = 0.25 * em
        self._left_panel = gui.Vert(0, gui.Margins(size, size, size, size))

        self.buttons_to_bar()

        self.distance_text_label = self.create_distance_label()
        self._left_panel.add_child(self.distance_text_label)

        w.set_on_layout(self._on_layout)
        w.add_child(self._scene)
        w.add_child(self._left_panel)

    def _start_measure_event(self, event):
        # CTRL + Left click
        if (event.type == gui.MouseEvent.Type.BUTTON_DOWN and
                event.is_button_down(gui.MouseButton.LEFT) and
                event.is_modifier_down(gui.KeyModifier.CTRL)):

            def calculate_distance_depth_image(depth_image):
                x = event.x - self._scene.frame.x
                y = event.y - self._scene.frame.y
                depth = np.asarray(depth_image)[y, x]
                self.process_points(x, y, depth)

            self._scene.scene.scene.render_to_depth_image(calculate_distance_depth_image)
            return gui.Widget.EventCallbackResult.HANDLED

        # CTRL + Right click
        elif (event.type == gui.MouseEvent.Type.BUTTON_DOWN and
              event.is_button_down(gui.MouseButton.RIGHT) and
              event.is_modifier_down(gui.KeyModifier.CTRL)):

            self.remove_pick()
            return gui.Widget.EventCallbackResult.HANDLED

        return gui.Widget.EventCallbackResult.IGNORED

    def _calc_prefer_indicate(self, point):
        [k, idx, _] = self.pcd_kdtree.search_knn_vector_3d(point, 1)
        return idx[0]

    @staticmethod
    def calculate_distance(point1: list[float], point2: list[float]) -> float:
        point1 = np.array(point1)
        point2 = np.array(point2)
        return np.linalg.norm(point1 - point2)

    @staticmethod
    def create_distance_label() -> gui.Label:
        label = gui.Label("Distance: -- m")
        label.text_color = gui.Color(255.0, 255.0, 255.0)
        label.visible = False
        return label

    @staticmethod
    def run():
        gui.Application.instance.run()

    def update_ply_scan_view(self, button_id):
        button_clicked = self.button_is_clicked_mapper[button_id]

        geometry_name = "pcd"
        scene = self._scene.scene
        pcd = o3d.io.read_point_cloud(PLY_FILE_PATH)

        material = rendering.MaterialRecord()
        material.point_size = 5.0

        if button_clicked:
            scene.add_geometry(geometry_name, pcd, material)
        else:
            scene.remove_geometry(geometry_name)

    def remove_pick(self):
        if self._picked_num > 0:
            idx = self._picked_indicates.pop()
            point = self._picked_positions.pop()

            print(
                f"Undo pick: #{idx} at ({point[0]}, {point[1]}, {point[2]})")

            self._scene.scene.remove_geometry(
                'sphere' + str(self._picked_num))
            self._picked_num -= 1
            self._scene.force_redraw()
        else:
            print('Undo nothing!')

    def process_points(self, x, y, z):
        NULL_DEPTH = 1.0
        if z == NULL_DEPTH:
            return
        world_coord = self._scene.scene.camera.unproject(
            x, y, z, self._scene.frame.width, self._scene.frame.height)
        idx = self._calc_prefer_indicate(world_coord)
        picked_point = np.asarray(self.pcd.points)[idx]

        self._picked_num += 1
        self._picked_indicates.append(idx)
        self._picked_positions.append(picked_point)

        if self._picked_num % 2 == 0:
            distance = self.calculate_distance(self._picked_positions[-1], self._picked_positions[-2])
            self.update_distance(distance)

    @staticmethod
    def exist_path(path: str) -> bool:
        return os.path.exists(path)

    # BUTTON FUNCTIONS
    def start_measure(self):
        if not self.exist_path(PLY_FILE_PATH):
            return
        visibility_after_click_mapper = {
            BUTTON_START_STREAM_ID: False,
            BUTTON_STOP_STREAM_ID: False,
            BUTTON_START_SCAN_ID: False,
            BUTTON_EXPORT_ID: False,
            BUTTON_START_MEASURE_ID: False,
            BUTTON_STOP_MEASURE_ID: True,
            BUTTON_SHOW_SCAN_ID: False,
            BUTTON_HIDE_SCAN_ID: False,
        }
        self.update_visiblity(visibility_after_click_mapper)

        self.distance_text_label.visible = True

        self.pcd = o3d.io.read_point_cloud(PLY_FILE_PATH)
        self.pcd_kdtree = o3d.geometry.KDTreeFlann(self.pcd)

        self._scene.set_on_mouse(self._start_measure_event)

        material = rendering.MaterialRecord()
        material.shader = SHADER_STYLE
        material.point_size = 5.0

        self._scene.scene.add_geometry(BUTTON_START_MEASURE_ID, self.pcd, material)

    def stop_measure(self):
        visibility_after_click_mapper = {
            BUTTON_START_STREAM_ID: False,
            BUTTON_STOP_STREAM_ID: False,
            BUTTON_START_SCAN_ID: False,
            BUTTON_EXPORT_ID: False,
            BUTTON_START_MEASURE_ID: True,
            BUTTON_STOP_MEASURE_ID: False,
            BUTTON_SHOW_SCAN_ID: False,
            BUTTON_HIDE_SCAN_ID: True,
        }
        self.update_visiblity(visibility_after_click_mapper)

        self.distance_text_label.visible = False
        self.distance_text_label.text = f"Distance -- m"

        self._scene.set_on_mouse(None)
        self._scene.scene.remove_geometry(BUTTON_START_MEASURE_ID)

    def show_ply_scene(self):
        if not self.exist_path(PLY_FILE_PATH):
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
        }
        self.update_visiblity(visibility_after_click_mapper)

        scene = self._scene.scene

        material = rendering.MaterialRecord()
        material.shader = SHADER_STYLE
        material.point_size = 5.0

        self.pcd = o3d.io.read_point_cloud(PLY_FILE_PATH)
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
        }
        self.update_visiblity(visibility_after_click_mapper)

        self.distance_text_label.visible = False

        scene = self._scene.scene
        scene.remove_geometry(MAIN_SCREEN_ID)

    def start_scan(self):
        from sensors.realsense_recorder import scan
        from src.run_system import get_pointcloud

        gui.Application.instance.post_to_main_thread(self.window, scan)

        # gui.Application.instance.post_to_main_thread(
        #            self.window, get_pointcloud)

        # get_pointcloud()

        pass  # todo

    def start_stream(self):
        visibility_after_click_mapper = {
            BUTTON_START_STREAM_ID: False,
            BUTTON_STOP_STREAM_ID: True,
            BUTTON_START_SCAN_ID: False,
            BUTTON_EXPORT_ID: False,
            BUTTON_START_MEASURE_ID: False,
            BUTTON_STOP_MEASURE_ID: False,
            BUTTON_SHOW_SCAN_ID: False,
            BUTTON_HIDE_SCAN_ID: False,
        }
        self.update_visiblity(visibility_after_click_mapper)

        self.button_is_clicked_mapper[BUTTON_STOP_STREAM_ID] = True

        geometry_name = "pcd"
        scene = self._scene.scene
        material = rendering.MaterialRecord()
        material.shader = SHADER_STYLE
        material.point_size = 5.0

        import pyrealsense2 as rs
        import threading
        from sensors.realsense_helper import get_profiles

        def add_and_clear(pcd):
            scene.clear_geometry()
            scene.add_geometry(geometry_name, pcd, material)

        def capture_frames():
            pipeline = rs.pipeline()
            config = rs.config()
            color_profiles, depth_profiles = get_profiles()

            # note: using 640 x 480 depth resolution produces smooth depth boundaries
            #       using rs.format.bgr8 for color image format for OpenCV based image visualization
            print('Using the default profiles: \n  color:{}, depth:{}'.format(
                color_profiles[0], depth_profiles[0]))
            w, h, fps, fmt = depth_profiles[0]
            config.enable_stream(rs.stream.depth, w, h, fmt, fps)
            w, h, fps, fmt = color_profiles[0]
            fmt = rs.format.bgr8
            config.enable_stream(rs.stream.color, w, h, fmt, fps)

            pipeline.start(config)

            align_to = rs.stream.color
            align = rs.align(align_to)

            try:
                while self.button_is_clicked_mapper[BUTTON_STOP_STREAM_ID]:
                    frames = pipeline.wait_for_frames()
                    aligned_frames = align.process(frames)

                    depth_frame = aligned_frames.get_depth_frame()
                    color_frame = aligned_frames.get_color_frame()
                    if not depth_frame or not color_frame:
                        continue

                    color_image = np.asanyarray(color_frame.get_data())

                    pc = rs.pointcloud()
                    pc.map_to(color_frame)
                    points = pc.calculate(depth_frame)

                    vertices = np.asanyarray(points.get_vertices()).view(np.float32).reshape(-1, 3)
                    colors = np.asanyarray(points.get_texture_coordinates()).view(np.float32).reshape(-1, 2)
                    vertices[:, 2] = -vertices[:, 2]

                    o3d_pc = o3d.geometry.PointCloud()
                    o3d_pc.points = o3d.utility.Vector3dVector(vertices)

                    color_data = []
                    for u, v in colors:
                        u = int(u * color_image.shape[1])
                        v = int(v * color_image.shape[0])
                        color_data_element = [0, 0, 0]
                        if 0 <= u < color_image.shape[1] and 0 <= v < color_image.shape[0]:
                            color_data_element = (color_image[v, u] / 255.0)
                            color_data_element[0], color_data_element[2] = color_data_element[2], color_data_element[0]
                        color_data.append(color_data_element)

                    o3d_pc.colors = o3d.utility.Vector3dVector(color_data)
                    R = o3d.geometry.get_rotation_matrix_from_xyz([0, 0, np.pi])
                    o3d_pc.rotate(R, center=(0, 0, 0))
                    if self.button_is_clicked_mapper[BUTTON_STOP_STREAM_ID]:
                        gui.Application.instance.post_to_main_thread(
                            self.window, lambda: add_and_clear(o3d_pc))

            finally:
                pipeline.stop()

        if self.button_is_clicked_mapper[BUTTON_STOP_STREAM_ID]:
            threading.Thread(target=capture_frames, daemon=True).start()

    def stop_stream(self):
        self.button_is_clicked_mapper[BUTTON_STOP_STREAM_ID] = False

        visibility_after_click_mapper = {
            BUTTON_START_STREAM_ID: True,
            BUTTON_STOP_STREAM_ID: False,
            BUTTON_START_SCAN_ID: True,
            BUTTON_EXPORT_ID: True,
            BUTTON_START_MEASURE_ID: False,
            BUTTON_STOP_MEASURE_ID: False,
            BUTTON_SHOW_SCAN_ID: True,
            BUTTON_HIDE_SCAN_ID: False,
        }
        self.update_visiblity(visibility_after_click_mapper)

        self._scene.scene.clear_geometry()

    def export_file(self):
        print("Exporting ply file...")
        visibility_after_click_mapper = {
            BUTTON_START_STREAM_ID: True,
            BUTTON_STOP_STREAM_ID: False,
            BUTTON_START_SCAN_ID: True,
            BUTTON_EXPORT_ID: True,
            BUTTON_START_MEASURE_ID: False,
            BUTTON_STOP_MEASURE_ID: False,
            BUTTON_SHOW_SCAN_ID: True,
            BUTTON_HIDE_SCAN_ID: False,
        }
        self.update_visiblity(visibility_after_click_mapper)
        self.location = os.getcwd()

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
        dlg.set_on_cancel(self._on_export_dialog_cancel)
        dlg.set_on_done(self._on_export_dialog_done)

        self.window.show_dialog(dlg)

        pass #todo
    

    
    def _on_export_dialog_done(self, filename):
        os.chdir(self.location)
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh("dataset/realsense/scene/integrated.ply")
        ms.save_current_mesh(filename)

        self.window.close_dialog()
        
    
    def _on_export_dialog_cancel(self):
        self.window.close_dialog()

def main():
    # We need to initialize the application, which finds the necessary shaders
    # for rendering and prepares the cross-platform window abstraction.

    w = AppWindow(2048, 768)
    w.run()


if __name__ == "__main__":
    main()
