#!/usr/bin/env python3
"""lazypush - stage, commit and push the current Git branch in one command."""
import os
import shutil
import subprocess
import sys

# Folders that should never be pushed. Shown in RED.
NEVER_PUSH_FOLDERS = ("node_modules/", "venv/")  # "venv/" also matches ".venv/"

# If any of these appear in a changed file's path, the push is treated as risky (RED).
RISKY_PATTERNS = [
    # keys and certificates
    ".pem", ".key", ".p12", ".pfx", ".jks", ".keystore", ".ppk",
    "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
    # passwords, tokens and config files that often hold them
    ".env", "secret.", "secrets.", "secret_key", "credentials.",
    "api_key", "apikey", "service-account",
    ".npmrc", ".pypirc", ".netrc", ".htpasswd", ".kdbx",
    ".tfstate", ".tfvars", ".aws/", ".ssh/",
] + list(NEVER_PUSH_FOLDERS)

# Template files are safe even if the name matches a risky pattern (.env.example).
SAFE_SUFFIXES = (".example", ".sample", ".template")

# Junk that usually does not belong in a repo. Shown in YELLOW (just a nudge).
# Written in .gitignore style: "name/" = folder anywhere, "*.ext" = extension, else exact file name.
JUNK_ENTRIES = [
    ".DS_Store", "Thumbs.db", "desktop.ini",
    "*.log", "*.tmp", "*.swp", "*.pyc", "__pycache__/", ".pytest_cache/",
    "*.sqlite", "*.sqlite3", "*.db",
    "build/", "dist/", "coverage/", ".idea/",
]

# GitHub rejects any single file over 100 MB.
BIG_FILE_BYTES = 100 * 1024 * 1024

# Status codes Git uses for files with unresolved merge conflicts.
CONFLICT_CODES = {"DD", "AU", "UD", "UA", "DU", "AA", "UU"}

# With more files than this, only the first ones are shown until the user presses "a".
SHOW_LIMIT = 10

RED = BOLD_RED = YELLOW = BOLD_YELLOW = RESET = ""  # filled in by setup_output()


def setup_output():
    """Make printing safe on Windows and turn on colors when the terminal supports them."""
    global RED, BOLD_RED, YELLOW, BOLD_YELLOW, RESET
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    if sys.stdout.isatty() and "NO_COLOR" not in os.environ:
        if os.name == "nt":
            os.system("")  # switches on ANSI colors in the Windows console
        RED, BOLD_RED = "\033[31m", "\033[1;31m"
        YELLOW, BOLD_YELLOW = "\033[33m", "\033[1;33m"
        RESET = "\033[0m"


def git(args, capture=True):
    """Runs a git command (no shell, so quotes in messages are safe)."""
    return subprocess.run(
        ["git"] + args,
        capture_output=capture,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def run_or_exit(args, fail_message):
    """Runs a git command with its output visible. Stops with fail_message if it fails."""
    if git(args, capture=False).returncode != 0:
        sys.exit(f"\n{fail_message}")


def get_path(status_line):
    """Pulls the file path out of a 'git status --porcelain' line."""
    path = status_line[3:]
    if " -> " in path:  # renamed files look like: old -> new
        path = path.split(" -> ")[-1]
    return path.strip().strip('"')


def is_deleted(status_line):
    return "D" in status_line[:2]


def is_risky(status_line):
    """True if this changed file looks like a secret or a never-push folder."""
    if is_deleted(status_line):  # deleting a risky file is not a risk
        return False
    path = get_path(status_line).lower()
    if path.endswith(SAFE_SUFFIXES):
        return False
    return any(pattern in path for pattern in RISKY_PATTERNS)


def junk_rule(status_line):
    """Returns the JUNK_ENTRIES rule this file matches, or None."""
    if is_deleted(status_line):
        return None
    path = get_path(status_line).lower()
    name = path.rsplit("/", 1)[-1]
    for entry in JUNK_ENTRIES:
        rule = entry.lower()
        if rule.endswith("/"):
            if path.startswith(rule) or "/" + rule in path:
                return entry
        elif rule.startswith("*."):
            if name.endswith(rule[1:]):
                return entry
        elif name == rule:
            return entry
    return None


def find_big_files(lines):
    """Returns (path, size) for every changed file over the GitHub limit."""
    root = git(["rev-parse", "--show-toplevel"]).stdout.strip()
    big = []
    for line in lines:
        if is_deleted(line):
            continue
        path = get_path(line)
        try:
            size = os.path.getsize(os.path.join(root, path))
        except OSError:
            continue
        if size > BIG_FILE_BYTES:
            big.append((path, size))
    return big


def print_files(entries, limit=None):
    """Prints (line, color) pairs. With a limit, the rest is summarized."""
    shown = entries if limit is None else entries[:limit]
    for line, color in shown:
        end = RESET if color else ""
        print(f"  {color}{line}{end}")
    if limit is not None and len(entries) > limit:
        print(f"  ...and {len(entries) - limit} more")


def confirm(question, default_yes, entries):
    """Asks y/n. Enter gives the default. 'a' shows the whole file list when it was cut short."""
    shown_all = len(entries) <= SHOW_LIMIT
    options = "[Y/n]" if default_yes else "[y/N]"
    while True:
        hint = "" if shown_all else f" (press a to show all {len(entries)} files)"
        answer = input(f"{question} {options}{hint}: ").strip().lower()
        if answer in ("a", "all") and not shown_all:
            print("\nAll files:")
            print_files(entries)
            print("-" * 40)
            shown_all = True
            continue
        if answer == "":
            return default_yes
        return answer in ("y", "yes")


def main():
    setup_output()

    # 1. Check Git, the repo, the branch and the remote
    if shutil.which("git") is None:
        sys.exit("Git is not installed.")

    check = git(["rev-parse", "--is-inside-work-tree"])
    if check.returncode != 0:
        if "not a git repository" in check.stderr.lower():
            sys.exit("Not inside a Git repository. Go to your project folder or run 'git init' first.")
        sys.exit(f"Git error: {check.stderr.strip()}")

    branch = git(["symbolic-ref", "--short", "-q", "HEAD"]).stdout.strip()
    if not branch:
        sys.exit(
            "You are on a detached HEAD (not on any branch).\n"
            "Create a branch first: git checkout -b my-branch\n"
            "If you are in the middle of a rebase or merge, finish it first\n"
            "(git rebase --continue or git rebase --abort)."
        )

    if "origin" not in git(["remote"]).stdout.split():
        sys.exit("No 'origin' remote found. Add it with: git remote add origin <your-github-url>")

    # 2. Look at the changes
    status = git(["-c", "core.quotepath=false", "status", "--porcelain", "-uall"])
    if status.returncode != 0:
        sys.exit(f"Git error: {status.stderr.strip()}")
    lines = status.stdout.rstrip().splitlines()

    if any(line[:2] in CONFLICT_CODES for line in lines):
        sys.exit("Some files have unresolved merge conflicts. Fix them first, then run lazypush again.")

    msg = " ".join(sys.argv[1:]).strip()

    if lines:
        # 3. Files over 100 MB: GitHub would reject the push, so stop before committing
        big = find_big_files(lines)
        if big:
            print(f"{BOLD_RED}FILE TOO BIG FOR GITHUB{RESET}")
            for path, size in big[:SHOW_LIMIT]:
                print(f"  {RED}{path} ({size / 1024 / 1024:.0f} MB){RESET}")
            if len(big) > SHOW_LIMIT:
                print(f"  ...and {len(big) - SHOW_LIMIT} more")
            print("GitHub rejects files over 100 MB. Nothing was committed.")
            print("Remove the file or add it to .gitignore, then run lazypush again.")
            print("(Already-tracked files also need 'git rm --cached <file>'.)")
            sys.exit(1)

        # 4. Sort the changes: risky (red), junk (yellow), everything else
        risky, junk, normal = [], [], []
        for line in lines:
            if is_risky(line):
                risky.append(line)
            elif junk_rule(line):
                junk.append(line)
            else:
                normal.append(line)
        # Secrets go first, so never-push folders (thousands of files) cannot push them out of view.
        risky.sort(key=lambda line: any(f in get_path(line).lower() for f in NEVER_PUSH_FOLDERS))
        entries = (
            [(line, RED) for line in risky]
            + [(line, YELLOW) for line in junk]
            + [(line, "") for line in normal]
        )

        # 5. Preview and confirm
        print(f"Branch: {branch}")
        print(f"Files to be staged and pushed ({len(lines)}):")
        print("-" * 40)
        if risky:
            print(f"{BOLD_RED}RISKY PUSH DETECTED{RESET}")
        print_files(entries, SHOW_LIMIT)
        print("-" * 40)

        if risky:
            print(f"{BOLD_RED}RISKY PUSH DETECTED{RESET}")
            print(f"{len(risky)} risky file(s) found. Go up and review the red files above.")
            print("To skip them: add them to .gitignore. (Already-tracked files also need")
            print("'git rm --cached <file>'.) Then run lazypush again.")
        if junk:
            rules = sorted({junk_rule(line) for line in junk})
            print(f"{BOLD_YELLOW}JUNK FILES DETECTED{RESET}")
            print(f"{len(junk)} file(s) usually do not belong in a repo (yellow above).")
            print("Consider adding these lines to .gitignore:")
            for rule in rules:
                print(f"  {YELLOW}{rule}{RESET}")

        if risky:
            ok = confirm("Push anyway?", False, entries)
        else:
            ok = confirm(f"Commit and push to origin/{branch}?", True, entries)
        if not ok:
            sys.exit("Cancelled. Nothing was committed or pushed.")

        # 6. Commit message, stage, commit
        if not msg:
            msg = input("Commit message: ").strip()
            if not msg:
                sys.exit("Commit message cannot be empty.")

        run_or_exit(["add", "-A"], "Staging failed. See the message above.")
        run_or_exit(
            ["commit", "-m", msg],
            "Commit failed. See the message above.\n"
            "If Git says 'Author identity unknown', run these once:\n"
            '  git config --global user.name "Your Name"\n'
            '  git config --global user.email "you@example.com"',
        )
    else:
        if git(["rev-parse", "--verify", "--quiet", "HEAD"]).returncode != 0:
            sys.exit("Nothing to commit and no commits yet.")
        print("Nothing new to commit. Pushing any existing commits...")

    # 7. Push (-u is harmless if the branch already tracks origin)
    print(f"\nPushing to origin/{branch}...")
    run_or_exit(
        ["push", "-u", "origin", branch],
        "Push failed. Your commit is saved locally.\n"
        "If GitHub rejected it because someone else pushed first, run:\n"
        f"  git pull --rebase origin {branch}\n"
        "then run lazypush again. (lazypush never force-pushes.)",
    )
    print(f"\nDone! Pushed to origin/{branch}.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by Ctrl+C.")
        sys.exit(130)
    except EOFError:
        print("\nStopped: input was closed.")
        sys.exit(1)