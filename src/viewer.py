import open3d as o3d

pcd = o3d.io.read_point_cloud("dataset/realsense/scene/integrated.ply")

vis = o3d.visualization.VisualizerWithEditing()
vis.create_window()
vis.add_geometry(pcd)
vis.run()
vis.destroy_window()
