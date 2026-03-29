from pathlib import Path
from dataclasses import dataclass, field
import os
import hashlib
import zlib
from abc import abstractmethod, ABC
from .constants import pygit_path


def read_ojbect(sha: str) -> tuple[str, bytes]:
    """функция которая декомпрессирует содержимое objects потом декодирует
     возвращает тип обьекта и его тело(sha, author....) """
    cat, name = sha[:2], sha[2:]

    with open(pygit_path / "objects" / cat / name, "rb") as file:
        content = file.read()
        decomp = zlib.decompress(content)
        idx_0_byts = decomp.index(b"\x00")
        header = decomp[:idx_0_byts].decode("utf-8")
        body = decomp[idx_0_byts+1:]

        obj_type, _ = header.strip().split()

        return obj_type, body


class GitObject(ABC):
    """абстрактный класс"""

    @abstractmethod
    def serialize(self) -> bytes:
        raise NotImplementedError

    def deserialize(self, data: bytes) -> "Blob":
        raise NotImplementedError


@dataclass
class Blob(GitObject):
    """класс блоб
    содержит байты содержимого файла(оборачивает их в обьект)"""
    data: bytes

    def serialize(self) -> bytes:
        return self.data

    @classmethod
    def deserialize(cls, data: bytes) -> "Blob":
        """переводит содержимое файла в байты"""
        # data = self.data
        # decoded_data = data.decode("utf-8")
        # return decoded_data
        return cls(data=data)


@dataclass
class Tree(GitObject):
    """класс дерева
    хранит указатели на блоб и tree обьекты
    запись состоит из mode, object_type, sha, filename/subdir
    """
    entires: list[tuple[str, str, str]] = field(default_factory=list)

    def serialize(self) -> bytes:
        """создает бинарную запись для tree"""
        tree_in_bytes = b""
        ent = self.entires

        for idx in range(len(ent)):
            binar_line = b""
            mode = ent[idx][0]
            path = ent[idx][1]
            sha = ent[idx][2]
            binar_path = path.encode("utf-8")
            binar_mode = mode.encode("utf-8")
            binar_sha = bytes.fromhex(sha)
            binar_line = binar_mode + b" " + binar_path + b"\x00" + binar_sha
            tree_in_bytes = tree_in_bytes+binar_line
        return tree_in_bytes

    @classmethod
    def deserialize(self) -> None:
        pass


@dataclass
class Commit(GitObject):
    """класс коммита
    собирает текст из полей
    если коммит первый то parent NONE!!
    """
    tree: str
    author: str
    commit_time: str
    parent: str | None
    commit_message: str

    def serialize(self) -> bytes:
        """собирает строчку для коммита"""
        comit_line = ""
        commit_time = self.commit_time
        parent = self.parent
        commit_message = self.commit_message
        author = self.author

        tree = "tree " + str(self.tree)
        author = "author " + str(author)
        commit_time = str(commit_time)
        if parent is not None:
            parent = "parent " + str(parent)
            comit_line = (comit_line +
                          tree +
                          "\n" +
                          parent +
                          "\n" +
                          author +
                          " " +
                          commit_time +
                          "\n" +
                          "\n" +
                          commit_message +
                          "\n")
        else:
            comit_line = (comit_line +
                          tree +
                          "\n" +
                          author +
                          " " +
                          commit_time +
                          "\n" + "\n" +
                          commit_message +
                          "\n")
        comit_line_b = comit_line.encode("utf-8")
        return comit_line_b

    @classmethod
    def deserialize(cls, decomp: bytes) -> "Commit":
        """разбирает строчку коммита
        принимает байты и декодирует их
        получаются новые поля с типом commit они и возвращаются
        """
        decomp = decomp.decode("utf-8")
        header, message = decomp.split("\n\n", 1)

        commit_message = message.strip()

        tree = ""
        parent = None or ""
        author = ""
        commit_time = ""

        for line in header.splitlines():
            if "tree " in line:
                tree = line[len("tree "):].strip()

            elif "parent " in line:
                parent = line[len("parent "):].strip()
            elif "author " in line:
                author, commit_time = (line[len("author "):]
                                       .strip()
                                       .rsplit(" ", 1))
        return cls(tree=tree, author=author, commit_time=commit_time,
                   parent=parent,
                   commit_message=commit_message)


def hash_object(data: bytes, obj_type: str) -> str:
    """функция хэширования
    берет тип обьекта и колличество данных
    вычисляет sha1
    потом сохраняет сжатые данные в objects """
    zag = f"{obj_type} {len(data)}\0"
    sha = zag.encode("utf-8") + data
    commp_sha = zlib.compress(sha)

    hassh = hashlib.sha1(sha)
    hassh = str(hassh.hexdigest())
    obj_path = Path(".pygit/objects/")
    os.makedirs(obj_path / hassh[0:2], exist_ok=True)

    os.chmod(obj_path / hassh[0:2], 0o777)
    (obj_path / hassh[0:2] / hassh[2:]).write_bytes(commp_sha)
    return hassh
