#!/usr/bin/env python3
import subprocess
import sys


def run(cmd):
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)


def get_current_branch():
    result = subprocess.run(
        ["git", "symbolic-ref", "--short", "-q", "HEAD"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def has_upstream():
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def main():
    # 1. Get commit message from terminal arguments or ask for it
    msg = " ".join(sys.argv[1:]).strip()
    if not msg:
        msg = input("Commit message: ").strip()
        if not msg:
            print("Commit message cannot be empty.")
            sys.exit(1)

    # 2. Check current branch
    branch = get_current_branch()
    if not branch:
        print("Error: Not inside a Git repository or currently on a detached HEAD.")
        sys.exit(1)

    # 3. Stage, commit, and push to current branch
    run(["git", "add", "."])
    run(["git", "commit", "-m", msg])

    if has_upstream():
        run(["git", "push", "origin", branch])
    else:
        run(["git", "push", "-u", "origin", branch])


if __name__ == "__main__":
    main()