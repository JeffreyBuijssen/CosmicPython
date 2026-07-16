from __future__ import annotations
import hashlib
import os
import shutil
from pathlib import Path


BLOCKSIZE = 65536

def hash_file(path):
    hasher = hashlib.sha1()
    with path.open("rb") as file:
        buf = file.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)
    return hasher.hexdigest()

def read_paths_and_hashes(root:str):
    hashes = {}
    for folder, _, files in os.walk(root):
        for file_name in files:
            hashes[hash_file(Path(folder) / file_name)] = file_name
    return hashes

def determine_actions(source_hashes, dest_hashes, source_folder, dest_folder):
    for sha, filename in source_hashes.items():
        if sha not in dest_hashes:
            sourcepath = Path(source_folder) / filename
            destpath = Path(dest_folder) / filename
            yield "COPY", sourcepath, destpath

        elif dest_hashes[sha] != filename:
            olddestpath = Path(dest_folder) / dest_hashes[sha]
            newdestpath = Path(dest_folder) / filename
            yield "MOVE", olddestpath, newdestpath

    for sha, filename in dest_hashes.items():
        if sha not in source_hashes:
            yield "DELETE", dest_folder / filename

def sync(source, dest, filesystem=FileSystem()):
    # imperative shell step 1, gather inputs
    # source_hashes = read_paths_and_hashes(source)
    # dest_hashes = read_paths_and_hashes(dest)
    source_hashes = filesystem.read(source)
    dest_hashes = filesystem.read(dest)


    # step 2: call functional core
    actions = determine_actions(source_hashes, dest_hashes, source, dest)

    # emerative shell step 3, apply outputs
    for action, *paths in actions:
        if action == "COPY":
            filesystem.copy(*paths)
        if action == "MOVE":
            # shutil.move(*paths)
            filesystem.move(*paths)
        if action == "DELETE":
            # os.remove(paths[0])
            filesystem.delete(*paths)

# def sync(source, dest):
#     # imperative shell step 1, gather inputs
#     source_hashes = read_paths_and_hashes(source)
#     dest_hashes = read_paths_and_hashes(dest)
    
#     # step 2: call functional core
#     actions = determine_actions(source_hashes, dest_hashes, source, dest)
#     for folder, _, files in os.walk(source):
#         for file_name in files:
#             source_hashes[hash_file(Path(folder) / file_name)] = file_name


#     # Walk the target folder and get the filenames and hashes
#     for folder, _, files in os.walk(dest):
#         for file_name in files:
#             dest_path = Path(folder) / file_name
#             dest_hash = hash_file(dest_path)
#             seen.add(dest_hash)

#             # if there's a file in target that's not in sourc, delete it
#             if dest_hash not in source_hashes:
#                 dest_path.remove()

#             # if there's a file in target that has a different path in source,
#             # move it to the correct path
#             elif dest_hash in source_hashes and file_name != source_hashes[dest_hash]:
#                 shutil.move(dest_path, Path(folder) / source_hashes[dest_hash])

#     # for every file that appears in source but not target, copy file to
#     # the target
#     for source_hash, file_name in source_hashes.items():
#         if source_hash not in seen:
#             shutil.copy(Path(source) / file_name, Path(dest) / file_name)

class FileSystem:

    def __init__(self):
        pass

    def read(self, path):
        return read_paths_and_hashes(path)
    
    def copy(self, source, dest):
        shutil.copyfile(source, dest)

    def move(self, source, dest):
        shutil.move(source,dest)

    def delete(self, dest):
        os.remove(dest)