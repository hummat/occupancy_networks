import argparse
import os
from joblib import Parallel, delayed
import pymeshlab
from tqdm import tqdm
from glob import glob


class RunMeshLabServerCommand:
    def __init__(self):
        parser = self.get_parser()
        self.options = parser.parse_args()
        self.is_glob = False

    @staticmethod
    def get_parser():
        parser = argparse.ArgumentParser(description='Scale a set of meshes stored as OFF files.')

        input_group = parser.add_mutually_exclusive_group(required=True)
        input_group.add_argument('--in_dir', type=str, help='Path to input directory or glob pattern.')
        input_group.add_argument('--in_path', type=str, help='Path to input file.')

        output_group = parser.add_mutually_exclusive_group(required=True)
        output_group.add_argument('--out_dir', type=str, help='Path to output directory.')
        output_group.add_argument('--out_path', type=str, help='Path to output file.')

        parser.add_argument('--script_path', type=str, help='Path to meshlabserver script.')
        parser.add_argument('--out_format', type=str)
        parser.add_argument('--out_name_pos', type=int, default=-1,
                            help='Position of the output name in the input path.')
        parser.add_argument('--n_proc', type=int, default=1, help='Number of processes to run in parallel')
        parser.add_argument('--use_pymeshlab', action='store_true')
        parser.add_argument('--overwrite', action='store_true', help='Overwrites existing files if true.')

        return parser

    @staticmethod
    def read_directory(directory):
        files = []
        for filename in os.listdir(directory):
            files.append(os.path.normpath(os.path.join(directory, filename)))
        return files

    def get_in_files(self):
        if self.options.in_dir:
            if os.path.isdir(self.options.in_dir):
                return self.read_directory(self.options.in_dir)
            self.is_glob = True
            return glob(self.options.in_dir)
        return [self.options.in_path]

    def run(self):
        if self.options.out_dir:
            os.makedirs(self.options.out_dir, exist_ok=True)
        files = self.get_in_files()
        tqdm_files = tqdm(files, disable=len(files) == 1)
        Parallel(n_jobs=min(self.options.n_proc, len(files)))(delayed(self.run_file)(file) for file in tqdm_files)

    def run_file(self, filepath):
        if self.options.out_dir:
            in_format = filepath.split('.')[-1]
            out_filename = filepath.split('/')[self.options.out_name_pos].split('.')[0]
            out_path = os.path.join(self.options.out_dir, out_filename + '.' + in_format)
            if self.options.out_format:
                out_path = out_path.replace(in_format, self.options.out_format)
        else:
            out_path = self.options.out_path

        if os.path.exists(out_path) and not self.options.overwrite:
            return

        if self.options.use_pymeshlab:
            ms = pymeshlab.MeshSet()
            ms.load_new_mesh(filepath)
            if self.options.script_path:
                ms.load_filter_script(self.options.script_path)
                ms.apply_filter_script()
            ms.save_current_mesh(file_name=out_path,
                                 save_vertex_color=False,
                                 save_vertex_coord=False,
                                 save_face_color=False,
                                 save_polygonal=False)
        else:
            os.system('meshlabserver -i %s -o %s -s %s' % (filepath, out_path, self.options.script_path))


if __name__ == '__main__':
    app = RunMeshLabServerCommand()
    app.run()
