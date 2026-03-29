from pathlib import Path
from collections.abc import Callable
pygit_dir = ".pygit"
pygit_path = Path(pygit_dir)

cat_object = "objects"
cat_head = "heads"
cat_refs = "refs"
file_HEAD = "HEAD"

path_to_index = Path(".pygit") / "index"
COMMANDS: dict[str, Callable[..., None]] = {}
