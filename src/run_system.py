# ----------------------------------------------------------------------------
# -                        Open3D: www.open3d.org                            -
# ----------------------------------------------------------------------------
# Copyright (c) 2018-2024 www.open3d.org
# SPDX-License-Identifier: MIT
# ----------------------------------------------------------------------------

# examples/python/reconstruction_system/run_system.py

import json
import argparse
import time
import datetime
import os, sys
from os.path import isfile

import open3d as o3d

from src.open3d_example import check_folder_structure

from src.initialize_config import initialize_config, dataset_loader

def get_pointcloud():
    # load dataset and check folder structure

    with open("config/realsense.json") as json_file:
        config = json.load(json_file)
        initialize_config(config)
        check_folder_structure(config['path_dataset'])


    assert config is not None
    print("====================================")
    print("Configuration")
    print("====================================")
    for key, val in config.items():
        print("%40s : %s" % (key, str(val)))

    times = [0, 0, 0, 0]
    start_time = time.time()
    import src.make_fragments
    src.make_fragments.run(config)
    times[0] = time.time() - start_time

    start_time = time.time()
    import src.register_fragments
    src.register_fragments.run(config)
    times[1] = time.time() - start_time

    start_time = time.time()
    import src.refine_registration
    src.refine_registration.run(config)
    times[2] = time.time() - start_time

    start_time = time.time()
    import src.integrate_scene
    src.integrate_scene.run(config)
    times[3] = time.time() - start_time



    print("====================================")
    print("Elapsed time (in h:m:s)")
    print("====================================")
    print("- Making fragments    %s" % datetime.timedelta(seconds=times[0]))
    print("- Register fragments  %s" % datetime.timedelta(seconds=times[1]))
    print("- Refine registration %s" % datetime.timedelta(seconds=times[2]))
    print("- Integrate frames    %s" % datetime.timedelta(seconds=times[3]))
    #print("- SLAC                %s" % datetime.timedelta(seconds=times[4]))
    #print("- SLAC Integrate      %s" % datetime.timedelta(seconds=times[5]))
    print("- Total               %s" % datetime.timedelta(seconds=sum(times)))
    sys.stdout.flush()

#get_pointcloud()