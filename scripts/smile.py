import os

import numpy as np
import torch
import trimesh

from im2mesh import config
from im2mesh.utils import binvox_rw, voxels
from im2mesh.checkpoints import CheckpointIO
from im2mesh.utils.visualize import visualize_pointcloud, visualize_voxels


def load_binvox(file_path: str):
    with open(file_path, "rb") as f:
        voxels_in = binvox_rw.read_as_3d_array(f)
    return voxels_in.data.astype(np.float32)


def load_pointcloud(file_path):
    pointcloud_dict = np.load(file_path)
    return pointcloud_dict['points'].astype(np.float32)


def load_mesh(file_path: str, process: bool = True, padding: float = 0.1):
    mesh = trimesh.load(file_path, process=False)

    if process:
        total_size = (mesh.bounds[1] - mesh.bounds[0]).max()
        scale = total_size / (1 - padding)
        centers = (mesh.bounds[1] + mesh.bounds[0]) / 2

        mesh.apply_translation(-centers)
        mesh.apply_scale(1 / scale)

    return mesh


def process_mesh(mesh, padding: float = 0, flip_yz: bool = False, with_transforms: bool = False):
    bbox = mesh.bounding_box.bounds
    loc = (bbox[0] + bbox[1]) / 2
    scale = (bbox[1] - bbox[0]).max() / (1 - padding)

    mesh.apply_translation(-loc)
    mesh.apply_scale(1 / scale)

    if flip_yz:
        angle = 90 / 180 * np.pi
        R = trimesh.transformations.rotation_matrix(angle, [1, 0, 0])
        mesh.apply_transform(R)

    if with_transforms:
        return mesh, loc, scale
    return mesh


def visualize_all(file_path):
    visualize_pointcloud(load_pointcloud(os.path.join(file_path, "points.npz")), show=True)
    visualize_voxels(load_binvox(os.path.join(file_path, "model.binvox")), show=True)


def visualize_from_mesh(file_path: str, flip_yz: bool = False, use_trimes: bool = False):
    mesh = load_mesh(file_path)
    mesh, loc, scale = process_mesh(mesh, flip_yz=flip_yz, with_transforms=True)

    pointcloud = mesh.sample(2048).astype(np.float32)

    if use_trimes:
        voxel = trimesh.exchange.binvox.voxelize_mesh(mesh,
                                                      dimension=32,
                                                      remove_internal=False,
                                                      center=True,
                                                      binvox_path="/home/matthias/Downloads/binvox")

        binvox = trimesh.exchange.binvox.export_binvox(voxel)  # Writes in 'xzy' format by default
        with open("viz.binvox", "wb") as f:
            f.write(binvox)
    else:
        voxels_occ = voxels.voxelize_ray(mesh, 32)
        voxels_out = binvox_rw.Voxels(voxels_occ, (32,) * 3,
                                      translate=loc, scale=scale,
                                      axis_order="xyz")  # 'xyz' means 'voxel_occ' is in this format
        with open("viz.binvox", "wb") as f:
            voxels_out.write(f)  # Always writes in 'xzy' format

    with open("viz.binvox", "rb") as f:
        voxels_in = binvox_rw.read_as_3d_array(f)  # Expects data in 'xzy' format (otherwise set 'fix_coords' to 'False'
    voxels_in = voxels_in.data.astype(np.float32)

    visualize_pointcloud(pointcloud, show=True)
    visualize_voxels(voxels_in, show=True)


def from_pointcloud(visualize=False):
    path_prefix = "/home/matthias/Data/Ubuntu/git/occupancy_networks"
    default_path = os.path.join(path_prefix, "configs/default.yaml")
    model_path = os.path.join(path_prefix, "configs/pointcloud/onet_pretrained.yaml")
    cfg = config.load_config(model_path, default_path)
    device = torch.device("cuda")

    mesh = load_mesh("/home/matthias/Data/Ubuntu/data/aae_workspace/models/case.ply")
    # mesh = load_mesh(os.path.join(path_prefix, "data/ShapeNet.build/03797390/2_watertight/cc5b14ef71e87e9165ba97214ebde03.off"))
    mesh = process_mesh(mesh, flip_yz=True)

    points = mesh.sample(100000).astype(np.float32)
    side = np.random.randint(3)
    xb = [points[:, side].min(), points[:, side].max()]
    length = np.random.uniform(0.7 * (xb[1] - xb[0]), (xb[1] - xb[0]))
    ind = (points[:, side] - xb[0]) <= length
    points = points[ind]

    indices = np.random.randint(points.shape[0], size=300)
    points = points[indices, :]
    noise = 0.005 * np.random.randn(*points.shape)
    noise = noise.astype(np.float32)
    points = points + noise

    if visualize:
        # visualize_pointcloud(points, show=True)
        trimesh.PointCloud(points).show()
    data = {'inputs': torch.unsqueeze(torch.from_numpy(points), dim=0)}

    model = config.get_model(cfg, device)
    checkpoint_io = CheckpointIO("..", model=model)
    # checkpoint_io.load(os.path.join(path_prefix, cfg['test']['model_file']))
    checkpoint_io.load(cfg['test']['model_file'])
    model.eval()

    generator = config.get_generator(model, cfg, device)
    mesh = generator.generate_mesh(data, return_stats=False)

    if visualize:
        mesh.show()
    else:
        mesh.export("smile.off")


def from_voxel_grid(use_trimesh: bool = True):
    path_prefix = "/home/matthias/Data/Ubuntu/git/occupancy_networks"
    default_path = os.path.join(path_prefix, "configs/default.yaml")
    model_path = os.path.join(path_prefix, "configs/voxels/onet_pretrained.yaml")
    cfg = config.load_config(model_path, default_path)
    device = torch.device("cuda")

    # mesh = load_mesh("/home/matthias/Data/Ubuntu/data/aae_workspace/models/case.ply")
    # mesh = load_mesh(os.path.join(path_prefix, "data/ShapeNet.build/02876657/2_watertight/1ae823260851f7d9ea600d1a6d9f6e07.off"))
    # mesh, loc, scale = process_mesh(mesh, with_transforms=True, flip_yz=False)
    # assert mesh.is_watertight
    #
    # if use_trimesh:
    #     voxel = trimesh.exchange.binvox.voxelize_mesh(mesh,
    #                                                   dimension=32,
    #                                                   remove_internal=False,
    #                                                   center=True,
    #                                                   binvox_path="/home/matthias/Downloads/binvox")
    #
    #     binvox = trimesh.exchange.binvox.export_binvox(voxel)
    #     with open("smile.binvox", "wb") as f:
    #         f.write(binvox)
    # else:
    #     voxels_occ = voxels.voxelize_ray(mesh, 32)
    #     voxels_out = binvox_rw.Voxels(voxels_occ, (32,) * 3,
    #                                   translate=loc, scale=scale,
    #                                   axis_order="xyz")  # 'xyz' means 'voxel_occ' is in this format
    #     with open("smile.binvox", "wb") as f:
    #         voxels_out.write(f)  # Always writes in 'xzy' format
    #
    # with open("smile.binvox", "rb") as f:
    #     voxels_in = binvox_rw.read_as_3d_array(f)

    # with open(os.path.join(path_prefix, "data/ShapeNet/02958343/1a0bc9ab92c915167ae33d942430658c/model.binvox"), "rb") as f:
    #     voxels_in = binvox_rw.read_as_3d_array(f)
    #
    # voxels_in = voxels_in.data.astype(np.float32)
    # visualize_voxels(voxels_in, show=True)
    # data = {'inputs': torch.unsqueeze(torch.from_numpy(voxels_in), dim=0)}

    dataset = config.get_dataset('test', cfg, return_idx=True)
    test_loader = torch.utils.data.DataLoader(dataset, batch_size=1, num_workers=0, shuffle=True)
    data = next(iter(test_loader))

    visualize_voxels(data["voxels"][0].cpu().numpy(), show=True)

    model = config.get_model(cfg, device, dataset)
    checkpoint_io = CheckpointIO("..", model=model)
    checkpoint_io.load(cfg['test']['model_file'])
    model.eval()

    generator = config.get_generator(model, cfg, device)
    mesh = generator.generate_mesh(data, return_stats=False)
    mesh.export("smile.off")


if __name__ == "__main__":
    from_pointcloud(visualize=True)
