from __future__ import annotations

import os
import pathlib
import shutil

import aiofiles

from src import secret
from .hash_tools import calc_sha1


def calc_hashed_filename(relative_path: pathlib.Path) -> str:
    suffix = str(relative_path.suffix)
    hashed_name = calc_sha1(secret.MEDIA_HASH_SALT + str(relative_path.with_suffix("")))
    return hashed_name + suffix


async def copy_file(source_path: str, destination_path: str) -> None:
    async with aiofiles.open(source_path, 'rb') as source_file:
        async with aiofiles.open(destination_path, 'wb') as destination_file:
            while True:
                chunk = await source_file.read(4096)
                if not chunk:
                    break
                await destination_file.write(chunk)


async def prepare_media_files() -> None:
    file_list: list[pathlib.Path] = []
    for root, t, files in os.walk(secret.MEDIA_PATH):
        for file in files:
            file_list.append(pathlib.Path(root + "/" + file).resolve())

    if secret.EXPORT_MEDIA_PATH.is_dir():
        shutil.rmtree(secret.EXPORT_MEDIA_PATH)
    os.makedirs(secret.EXPORT_MEDIA_PATH, exist_ok=True)
    print(secret.MEDIA_PATH)
    for filepath in file_list:
        relative_path = filepath.relative_to(secret.MEDIA_PATH)
        hashed_name = calc_hashed_filename(relative_path)
        target_file = secret.EXPORT_MEDIA_PATH / hashed_name
        print(f"copy {filepath} to {target_file}")
        if target_file.is_file():
            assert False, f"duplicate file! {str(target_file)}"
        await copy_file(str(filepath), str(target_file))


async def update_media_files() -> None:
    file_list: list[pathlib.Path] = []
    for root, t, files in os.walk(secret.MEDIA_PATH):
        for file in files:
            file_list.append(pathlib.Path(root + "/" + file).resolve())

    if not secret.EXPORT_MEDIA_PATH.is_dir():
        os.makedirs(secret.EXPORT_MEDIA_PATH, exist_ok=True)
    print(secret.MEDIA_PATH)
    for filepath in file_list:
        relative_path = filepath.relative_to(secret.MEDIA_PATH)
        hashed_name = calc_hashed_filename(relative_path)
        target_file = secret.EXPORT_MEDIA_PATH / hashed_name
        if not target_file.is_file():
            print(f"copy {filepath} to {target_file}")
            await copy_file(str(filepath), str(target_file))


def media_wrapper(file: str) -> str:
    """
        输入相对于 media 文件夹的路径
    """
    if secret.HASH_MEDIA_FILENAME:
        fullpath = (secret.MEDIA_PATH / file).resolve()
        relative_path = fullpath.relative_to(secret.MEDIA_PATH)
        hashed_name = calc_hashed_filename(relative_path)
        return "/m/" + hashed_name
    return "/media/" + file
