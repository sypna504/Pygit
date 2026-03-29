from .objects import Commit
from .objects import read_ojbect


class CommitHistoryIterator:
    """класс итератор показывающий историю коммитов
    читает objects десереализирует
    и выводит информацию по коммитам"""

    def __init__(self, init_sha: str) -> None:
        self.init_sha = init_sha

    def __iter__(self) -> "CommitHistoryIterator":
        return self

    def __next__(self) -> tuple[str, str, str]:
        if self.init_sha is None:
            raise StopIteration

        else:
            sha = self.init_sha
            object_type, body = read_ojbect(sha)
            commit = Commit.deserialize(body)
            if object_type == "commit":
                author = commit.author
                message = commit.commit_message
            else:
                raise StopIteration
            self.init_sha = commit.parent or None


        return sha, author, message
