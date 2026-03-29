import os
from pathlib import Path
from .objects import Blob, hash_object, Commit
from .index import read_index, write_index, path_to_index, create_tree
import time
import sys
from typing import TypeVar, Callable
from .log import CommitHistoryIterator
from .constants import *

F = TypeVar("F", bound=Callable[..., None])


def commands(name: str) -> Callable[[F], F]:
    """декоратор чтобы при вводе в консоль работали команды """
    def wrapper(func: F) -> F:

        COMMANDS[name] = func
        return func

    return wrapper


@commands("init")
def pygit_init(args: list[str] | None = None) -> None:
    """команда иницилизации репо
    создает каталоги файлы и ветку по деффолту main"""
    try:
        os.makedirs(pygit_path, exist_ok=True)
        os.makedirs(pygit_path / cat_object, exist_ok=True)
        os.makedirs(pygit_path / cat_refs / cat_head, exist_ok=True)
        (pygit_path / file_HEAD).write_text("ref: refs/heads/main")
        (pygit_path / cat_refs / cat_head / "main").write_text("")
        path_to_index.write_text("")
        print("каталог")
    except (FileExistsError, ValueError) as fail:
        print(fail)


@commands("add")
def pygit_add(args: list[str]) -> None:
    """функция сбора файлов в так называемый index
    перед коммитом
    переводит содержимое файла в блоб и хэширует
    сравнивает с текущим index либо изменяет либо добавляет
    """
    added_file = Path(args[0])
    file_mode = str(os.stat(added_file).st_mode)
    try:

        with open(added_file, "rb") as file:
            try:
                content = file.read()
                data = Blob(content).serialize()
                sha = hash_object(data, "blob")

            except (FileExistsError, FileNotFoundError) as fail:
                print(fail)

    except (FileExistsError, FileNotFoundError) as fail:
        print(fail)


    entries = read_index()
    flag = 0
    print(entries)
    for i, (path, _, _) in enumerate(entries):
        if Path(path) == added_file:
            entries[i] = (added_file, sha, file_mode)
            flag = 1
            break

    if flag == 0:
        entries.append((added_file, sha, file_mode))
    write_index(entries)


@commands("write-tree")
def pygit_write_tree(args: list[str] | None = None) -> None:
    """функция создания tree обьекта из индекса
    выводит sha корнегого дерева"""
    tree_sha = create_tree()
    print(tree_sha)


@commands("commit")
def pygit_commit(args: list[str]) -> None:
    """функция создания коммита на основе текущего индекса
    читает индекс делает структуру дирректорий и возвращает хэш 'снимка'
    по итогу сохраняет все в objects обновляя файл или создавая новый
    """
    m_index = args.index("-m")
    message_parts = args[m_index + 1:]
    commit_mesage = " ".join(message_parts)

    tree_sha = create_tree()

    with open(pygit_path / file_HEAD, "r") as file_Head:

        ref_path = file_Head.read().strip().split()[-1]
        tree_file_path = pygit_path / ref_path
        if os.path.exists(tree_file_path):

            with open(tree_file_path, "r") as tree_file:
                tree_file_cont = tree_file.read()
                if len(tree_file_cont) != 0:
                    parent_sha = tree_file_cont.strip()
                    parent = parent_sha

                else:
                    parent = None

        else:
            parent = None
    commit = Commit(tree_sha, "user@", str(time.time()), parent, commit_mesage)
    commit = commit.serialize()
    commit_sha = hash_object(commit, "commit")
    print(commit_sha)
    flag = 0
    with open(tree_file_path, "r") as tree_file:
        content = tree_file.read()
        if len(content) == 0:
            flag = 1
        else:
            flag = 0

    if flag == 1:
        with open(tree_file_path, "a") as tree_file:
            tree_file.write(commit_sha)
    else:
        with open(tree_file_path, "w") as tree_file:
            tree_file.write(commit_sha)


@commands("log")
def pygit_log(args: list[str] | None = None) -> None:
    """функция вывода логов коммита
    читает файл с коммитами и выводит их лог
    хэш автор и сообщение"""
    with open(pygit_path / file_HEAD, "r") as hd:
        content = hd.read().strip()
        ref_path = content.split()[-1]
        branch_file = pygit_path / ref_path

        if os.path.exists(branch_file) is False or not (branch_file
                                                        .read_text()
                                                        .strip()):
            print("empty")
            return
    start_sha = branch_file.read_text().strip()
    for commit_sha, author, message in CommitHistoryIterator(start_sha):
        print("sha:" + str(commit_sha))
        print("author:" + str(author))
        print("message:" + str(message))


"""ДЛЯ ТЕСТОВ """


def add(filename: str) -> None:
    pygit_add([filename])


def init() -> None:
    pygit_init()


def main(argv: list[str] | None = None) -> None:
    line = sys.argv
    cmd = line[1]
    args = line[2:]
    func = COMMANDS.get(cmd)
    func(args)


if __name__ == "__main__":
    main()
