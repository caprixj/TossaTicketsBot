from pathlib import Path
import sys

EXCLUDE_DIRS = {
    '.git', '.idea', '__pycache__', '.venv', 'venv', 'env', 'node_modules',
    '.mypy_cache', '.pytest_cache', '.egg-info', 'dist', 'build', '.eggs'
}
EXCLUDE_FILE_SUFFIXES = {'.pyc', '.pyo', '.egg-info'}


def should_exclude(path: Path):
    name = path.name
    if name in EXCLUDE_DIRS:
        return True
    if path.is_file():
        for s in EXCLUDE_FILE_SUFFIXES:
            if name.endswith(s):
                return True
    return False


def write_tree(root: Path, out_file: Path):
    def _write_dir(p: Path, prefix: str, f):
        try:
            entries = sorted([e for e in p.iterdir() if not should_exclude(e)], key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            f.write(prefix + "└── [permission denied]\n")
            return
        for i, entry in enumerate(entries):
            connector = '└── ' if i == len(entries) - 1 else '├── '
            display_name = entry.name + ('/' if entry.is_dir() else '')
            f.write(prefix + connector + display_name + '\n')
            if entry.is_dir():
                new_prefix = prefix + ('    ' if i == len(entries) - 1 else '│   ')
                _write_dir(entry, new_prefix, f)

    with out_file.open('w', encoding='utf-8') as f:
        f.write(str(root.resolve()) + '\n')
        _write_dir(root, '', f)


if __name__ == '__main__':
    # Allow optional path argument; default to repository root (two levels above this script)
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1]).resolve()
    out_path = repo_root / 'project_tree.txt'
    write_tree(repo_root, out_path)
    print(f'Wrote project tree to: {out_path}')
