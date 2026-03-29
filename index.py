from dataclasses import dataclass
from .objects import hash_object, Tree
from .constants import path_to_index


def read_index() -> list[str]:
    """читает содержимое файла index(заготовка перед коммитом)
    каждую строку превращает в path, sha, mode"""
    readed_index = []
    try:
        with open(path_to_index, "r") as index_file:
            content = index_file.readlines()
            for line in content:
                line = line.split()
                if len(line) == 0:
                    continue

                path, sha, mode = line
                # path = os.path.abspath(path)
                readed_index.append((path, sha, mode))
    except FileNotFoundError:
        return readed_index
    return readed_index


def write_index(entries: list[bytes, bytes, bytes]) -> None:
    """перезаписывает файл index"""
    with open(path_to_index, "w") as index_file:
        for path, sha, mode in entries:
            index_file.write(f"{path} {sha} {mode}" + "\n")


@dataclass
class Directories:
    """класс в качестве узла для tree обьектов"""
    name: str
    files: list[tuple[str, str, str]]
    subdirs: dict


def add__index(root: Directories, path: str, sha: str, mode: str) -> None:
    """добавляет запись из индекста в дерево директорий(root)
    проходится по всем дирректориям и создает поддиректории """
    patrs_of_paths = path.split('\\')
    dirs = patrs_of_paths[:-1]
    file = patrs_of_paths[-1]
    for dir_name in dirs:
        if dir_name not in root.subdirs.keys():
            root.subdirs[dir_name] = Directories(dir_name, [], {})
        root = root.subdirs[dir_name]
    root.files.append((file, sha, mode))


def dir_tree(root) -> None:
    """строит дерево дирректорий root по index
    создает новый корень и читает записи из индекса
    потом добавляет файлы в нужную дерикторию дерева"""
    root = Directories("", [], {})
    entries = read_index()
    for path, sha, mode in entries:
        add__index(root, path, sha, mode)


def generator(dir: Directories, path: str):
    """генератор который обходит дерево директорий
    начинает с потдиректорий
    и вычисляет новую потдиректорию
    """
    for dir_name, sub in sorted(dir.subdirs.items(), key=lambda x: x[0]):
        if len(path.split("\\")) == 1:
            sub_path = dir_name
        else:
            sub_path = path / str(dir_name)
        yield from generator(sub, sub_path)
    yield path, dir.files, list(dir.subdirs.keys())


def create_tree() -> str:
    """строит и сохраняет все tree обьекты"""
    dir_sha = dict()
    entries = read_index()
    root = Directories("", [], {})
    for elems in entries:
        path, sha, mode = elems
        add__index(root, path, sha, mode)

    for dir_path, files, subdir_names in generator(root, ""):
        tree_entr = []

        for dirname in subdir_names:
            if dir_path == "":
                sub_path = dirname
            else:
                sub_path = dir_path / dirname
            sub_sha = dir_sha[sub_path]
            tree_entr.append(("40000", dirname, sub_sha))

        for file, sha, mode in files:
            tree_entr.append((str(mode), file, sha))

        tree_object = Tree(tree_entr)
        tree_data = tree_object.serialize()
        tree_sha = hash_object(tree_data, "tree")

        dir_sha[dir_path] = tree_sha
    return dir_sha[""]
