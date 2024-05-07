import os
import random
import argparse
import shutil


def find_files(directory, extension):
    """Recursively find all files in the given directory with a specific extension."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                yield os.path.join(root, file)


def randomly_select_files(directory, num_files=1, extension=".00000"):
    """Randomly select a specified number of files with a specific extension from a directory, including its subdirectories."""
    all_files = list(find_files(directory, extension))
    if len(all_files) == 0:
        return []
    selected_files = random.sample(all_files, min(len(all_files), num_files))
    return selected_files


def copy_files(files, target_directory):
    """Copy selected files to the target directory."""
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
    for file in files:
        shutil.copy(file, target_directory)
        print(f"Copied {file} to {target_directory}")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=
        'Randomly select and copy files with a specific extension from a specified directory.'
    )
    parser.add_argument('directory',
                        type=str,
                        help='The directory to search for files.')
    parser.add_argument('num_files',
                        type=int,
                        help='The number of files to randomly select.')
    parser.add_argument('target_directory',
                        type=str,
                        help='The directory to copy the selected files to.')
    parser.add_argument('-e',
                        '--extension',
                        type=str,
                        default=".00000",
                        help='File extension to filter by (default is .00000)')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.num_files < 1:
        print("Please specify at least one file.")
    else:
        selected_files = randomly_select_files(args.directory, args.num_files,
                                               args.extension)
        if not selected_files:
            print("No files found with the specified extension.")
        else:
            print("Randomly selected files:")
            for file in selected_files:
                print(file)
            copy_files(selected_files, args.target_directory)
