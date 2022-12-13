import argparse
import ntpath
import os
import joblib

import common


class RunMeshLabServerCommand:
    """
    Perform MeshLab Server operation on inputs.
    """

    def __init__(self):
        """
        Constructor.
        """

        parser = self.get_parser()
        self.options = parser.parse_args()
        self.simplification_script = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.options.script)

    @staticmethod
    def get_parser():
        """
        Get parser of tool.

        :return: parser
        """

        parser = argparse.ArgumentParser(description='Scale a set of meshes stored as OFF files.')
        input_group = parser.add_mutually_exclusive_group(required=True)
        input_group.add_argument('--in_dir', type=str,
                                 help='Path to input directory.')
        input_group.add_argument('--in_file', type=str,
                                 help='Path to input file.')
        parser.add_argument('--script', type=str, required=True,
                            help='Name of meshlabserver script.')
        parser.add_argument('--out_dir', type=str,
                            help='Path to output directory; files within are overwritten!')
        parser.add_argument('--n_proc', type=int, default=0,
                            help='Number of processes to run in parallel'
                                 '(0 means sequential execution).')

        return parser

    @staticmethod
    def read_directory(directory):
        """
        Read directory.

        :param directory: path to directory
        :return: list of files
        """

        files = []
        for filename in os.listdir(directory):
            files.append(os.path.normpath(os.path.join(directory, filename)))

        return files

    def get_in_files(self):
        if self.options.in_dir is not None:
            assert os.path.exists(self.options.in_dir)
            common.makedir(self.options.out_dir)
            files = self.read_directory(self.options.in_dir)
        else:
            files = [self.options.in_file]

        return files

    def run(self):
        """
        Run simplification.
        """

        common.makedir(self.options.out_dir)
        files = self.get_in_files()

        if self.options.n_proc == 0:
            for filepath in files:
                self.run_file(filepath)
        else:
            joblib.Parallel(n_jobs=self.options.n_proc)(joblib.delayed(self.run_file)(filepath) for filepath in files)

    def run_file(self, filepath):
        os.system('meshlabserver -i %s -o %s -s %s' % (filepath, os.path.join(self.options.out_dir, ntpath.basename(filepath)), self.simplification_script))


if __name__ == '__main__':
    app = RunMeshLabServerCommand()
    app.run()