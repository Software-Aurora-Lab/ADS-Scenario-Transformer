import os
import shutil

def move_dir(source_dir, target_dir):
    if not os.path.exists(target_dir):
        shutil.copytree(source_dir, target_dir)


def delete_dir(dir_path, mk_dir):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    if mk_dir:
        os.makedirs(dir_path)

def move_file(source_dir, target_dir):
    if os.path.exists(target_dir):
        os.remove(target_dir)
    shutil.copy(source_dir, target_dir)