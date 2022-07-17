import os
import json
from pathlib import Path
from typing import Union, List, Any
from natsort import natsorted


def read_json(file_path: str) -> Any:
    """Return data from json file"""
    with open(file_path, "r") as f:
        try:
            file_data = json.load(f)
            return file_data
        except json.JSONDecodeError as e:
            print(e)


def collect_file_paths(
        path: str, suffixes: Union[List[str], List[str]] = None,
        flatten: bool = True, sort: bool = True) -> list:
    """Returns list of file_paths with matching suffixes"""
    suffixes = [] if suffixes is None else suffixes
    collected_file_paths = list()
    if not path:
        return collected_file_paths

    try:
        search_paths = os.listdir(path)
    except NotADirectoryError:
        search_paths = [path]
    except FileNotFoundError:
        search_paths = []

    for search_path in search_paths:
        abs_search_path = os.path.join(path, search_path)
        # If search path is a directory, then,
        # collect file paths from it and append to collection
        if os.path.isdir(abs_search_path):
            file_paths = collect_file_paths(
                path=abs_search_path,
                suffixes=suffixes,
                flatten=flatten
            )
            collected_file_paths += file_paths if flatten or not file_paths else [file_paths]
        # If search path is a file, then,
        # append directly to collection
        else:
            file_name = Path(abs_search_path).name
            if suffixes and not file_name.endswith(tuple(suffixes)):
                collected_file_paths += []
            else:
                collected_file_paths += [abs_search_path]
    if sort:
        collected_file_paths = natsorted(collected_file_paths)
    return collected_file_paths