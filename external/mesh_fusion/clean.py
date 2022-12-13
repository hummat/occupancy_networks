import argparse
import os
import joblib
import numpy as np
import trimesh
import gc


def run_file(in_dir, out_dir, file, overwrite=False):
    if not overwrite and os.path.exists(os.path.join(out_dir, file)):
        return
    try:
        mesh = trimesh.load(os.path.join(in_dir, file), process=False)
    except Exception as e:
        print(f"Exception {e} occurred when loading file {file}")
        del mesh
        return
    mesh_split = mesh.split()

    if len(mesh_split) > 1:
        num_vertices = [len(m.vertices) for m in mesh_split]
        print(f"Splitting {file} into {len(num_vertices)} meshes; Largest connected component has {max(num_vertices)} vertices")
        new_mesh = mesh_split[np.argmax(num_vertices)]
        if new_mesh.is_watertight:
            try:
                new_mesh.export(os.path.join(out_dir, file))
            except Exception as e:
                print(f"Exception {e} occurred when exporting new mesh for file {file}")
                mesh.export(os.path.join(out_dir, file))
        else:
            print(f"New mesh for {file} is not watertight")
            mesh.export(os.path.join(out_dir, file))
        del new_mesh
    else:
        mesh.export(os.path.join(out_dir, file))

    for m in mesh_split:
        del m
    del mesh
    gc.collect()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_dir', type=str, help='Path to input directory.')
    parser.add_argument('--n_proc', type=int, default=1,
                        help='Number of processes to run in parallel (0 means sequential execution).')
    parser.add_argument('--out_dir', type=str,
                        help='Path to output directory; files within are overwritten!')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files')
    args = parser.parse_args()

    files = os.listdir(args.in_dir)
    joblib.Parallel(n_jobs=args.n_proc)(joblib.delayed(run_file)(args.in_dir, args.out_dir, f, args.overwrite) for f in files)


if __name__ == '__main__':
    main()
