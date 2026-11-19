#!/usr/bin/env python3
"""lazypush - stage, commit and push the current Git branch in one command."""
import os
import shutil
import subprocess
import sys

# Junk folders that should never be pushed ("venv/" also matches ".venv/").
JUNK_FOLDERS = ("node_modules/", "venv/")

# If any of these appear in a changed file's path, the push is treated as risky.
RISKY_PATTERNS = [
    # keys and certificates
    ".pem", ".key", ".p12", ".pfx", ".jks", ".keystore", ".ppk",
    "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
    # passwords, tokens and config files that often hold them
    ".env", "secret.", "secrets.", "secret_key", "credentials.",
    "api_key", "apikey", "service-account",
    ".npmrc", ".pypirc", ".netrc", ".htpasswd", ".kdbx",
    ".tfstate", ".tfvars", ".aws/", ".ssh/",
] + list(JUNK_FOLDERS)

# Template files are safe even if the name matches a risky pattern (.env.example).
SAFE_SUFFIXES = (".example", ".sample", ".template")

# Status codes Git uses for files with unresolved merge conflicts.
CONFLICT_CODES = {"DD", "AU", "UD", "UA", "DU", "AA", "UU"}

# Only this many files are printed per group, so a huge folder does not flood the screen.
MAX_SHOWN = 40

RED = BOLD_RED = RESET = ""  # filled in by setup_output() when colors work


def setup_output():
    """Make printing safe on Windows and turn on colors when the terminal supports them."""
    global RED, BOLD_RED, RESET
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    if sys.stdout.isatty() and "NO_COLOR" not in os.environ:
        if os.name == "nt":
            os.system("")  # switches on ANSI colors in the Windows console
        RED, BOLD_RED, RESET = "\033[31m", "\033[1;31m", "\033[0m"


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


def ask(prompt, default_yes):
    """Asks a yes/no question. Pressing Enter gives the default answer."""
    answer = input(prompt).strip().lower()
    if answer == "":
        return default_yes
    return answer in ("y", "yes")


def get_path(status_line):
    """Pulls the file path out of a 'git status --porcelain' line."""
    path = status_line[3:]
    if " -> " in path:  # renamed files look like: old -> new
        path = path.split(" -> ")[-1]
    return path.strip().strip('"')


def is_risky(status_line):
    """True if this changed file looks like a secret or an unwanted folder."""
    if "D" in status_line[:2]:  # deleting a risky file is not a risk
        return False
    path = get_path(status_line).lower()
    if path.endswith(SAFE_SUFFIXES):
        return False
    return any(pattern in path for pattern in RISKY_PATTERNS)


def print_files(lines, color=""):
    """Prints up to MAX_SHOWN files, optionally in color."""
    end = RESET if color else ""
    for line in lines[:MAX_SHOWN]:
        print(f"  {color}{line}{end}")
    if len(lines) > MAX_SHOWN:
        print(f"  ...and {len(lines) - MAX_SHOWN} more")


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
        risky = [line for line in lines if is_risky(line)]
        safe = [line for line in lines if not is_risky(line)]
        # Secrets go first, so junk folders (thousands of files) never push them out of view.
        risky.sort(key=lambda line: any(j in get_path(line).lower() for j in JUNK_FOLDERS))

        # 3. Preview and confirm (risky files first, in red)
        print(f"Branch: {branch}")
        print("Files to be staged and pushed:")
        print("-" * 40)
        if risky:
            print(f"{BOLD_RED}RISKY PUSH DETECTED{RESET}")
            print_files(risky, RED)
        print_files(safe)
        print("-" * 40)

        if risky:
            print(f"{BOLD_RED}RISKY PUSH DETECTED{RESET}")
            print(f"{len(risky)} risky file(s) found. Go up and review the red files above.")
            print("To skip them: add them to .gitignore. (Already-tracked files also need")
            print("'git rm --cached <file>'.) Then run lazypush again.")
            if not ask("Push anyway? [y/N]: ", default_yes=False):
                sys.exit("Cancelled. Nothing was committed or pushed.")
        elif not ask(f"Commit and push to origin/{branch}? [Y/n]: ", default_yes=True):
            sys.exit("Cancelled. Nothing was committed or pushed.")

        # 4. Commit message, stage, commit
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

    # 5. Push (-u is harmless if the branch already tracks origin)
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