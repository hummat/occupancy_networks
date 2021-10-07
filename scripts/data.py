import time

import trimesh

if __name__ == "__main__":
    path = "../data/ShapeNet.build/02876657/2_watertight/1071fa4cddb2da2fc8724d5673a063a6.off"
    mesh = trimesh.load(path)

    binvoxer = trimesh.exchange.binvox.Binvoxer(binvox_path="/home/matthias/Downloads/binvox")
    voxel = trimesh.exchange.binvox.voxelize_mesh(mesh,
                                                  dimension=32,
                                                  remove_internal=True,
                                                  center=True,
                                                  binvox_path="/home/matthias/Downloads/binvox")
    binvox = trimesh.exchange.binvox.export_binvox(voxel, axis_order="xyz")
    with open("test.binvox", "wb") as f:
        f.write(binvox)
    with open("test.binvox", "rb") as f:
        voxel = trimesh.exchange.binvox.load_binvox(f, axis_order="xyz")
