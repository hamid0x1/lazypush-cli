# lazypush

Stage, commit and push your code to GitHub with **one command**.

```
lazypush fixed the login bug
```

That's it. lazypush runs `git add`, `git commit` and `git push` for you, and shows you what is about to be pushed first, so you don't accidentally upload passwords or junk files.

> **Windows 10/11 (64-bit) only for now.** Other systems will come later.

---

## What it does

When you run `lazypush`, it:

1. Checks that Git is installed and that you are inside a Git project.
2. Looks at what changed and shows you the list of files.
3. Warns you about risky files (passwords, keys), junk files, and files that are too big for GitHub.
4. Asks you to confirm. Press **Enter** to go ahead.
5. Adds everything, commits it with your message, and pushes to the branch you are on.

It never uses force-push, and it never switches or creates branches. It always pushes the branch you are currently on, to the remote named `origin`.

---

## Before you start

You need:

- **Windows 10 or 11, 64-bit**
- **Git** installed ([git-scm.com](https://git-scm.com/download/win))
- A Git project with a GitHub remote called `origin` (see [Setting up a new project](#setting-up-a-new-project))
- Git told who you are (one time only):
  ```
  git config --global user.name "Your Name"
  git config --global user.email "you@example.com"
  ```
- A GitHub login that works from Git. With an `https://` address, Git asks you to sign in through your browser (Git for Windows includes this). A GitHub password typed into the terminal will not work.

You do **not** need Python to use lazypush.

---

## Install

1. Download the latest zip from the **Releases** page of this repository.
2. Right-click the zip and choose **Extract All**. (Don't run files from inside the zip.)
3. Open the extracted folder and double-click **`install.bat`**.
4. Close any terminal windows that are open, then open a **new** one (Command Prompt, PowerShell or Windows Terminal).
5. Go to your project folder and type `lazypush`.

If Windows shows **"Windows protected your PC"**, click **More info**, then **Run anyway**. This happens because the files are not code-signed.

What the installer does:

- Copies `lazypush.exe` to `C:\Users\<you>\AppData\Local\Programs\lazypush`
- Adds that folder to your **user** PATH so the `lazypush` command works everywhere
- Does not need administrator rights and does not touch other users on the PC

After installing, **keep the extracted folder** (or at least `uninstall.bat`). It is the only file you will need later.

### Update

Download the new zip, extract it, and run `install.bat` again. It replaces the old version and does not add a second PATH entry. Close terminals that are using lazypush first.

### Uninstall

Run **`uninstall.bat`** from the extracted folder. It removes the program and its PATH entry. Open a new terminal afterwards.

Your projects and Git settings are not touched. If you deleted the folder, download the zip again and run `uninstall.bat` from it.

---

## How to use

Go to your project folder in a terminal and run:

| Command                      | What happens                                                                   |
| :--------------------------- | :----------------------------------------------------------------------------- |
| `lazypush your message here` | Shows the changes, asks to confirm, then commits with that message and pushes. |
| `lazypush`                   | Same, but asks you to type the commit message after you confirm.               |

You do not need quotes for a normal message:

```
lazypush hi everything is set and good
```

**Use quotes** if your message has special characters:

- Command Prompt: `&  |  <  >  ^  %` cause problems. Example: `lazypush "fix login & logout"`
- PowerShell: an apostrophe starts a quoted string. Example: `lazypush "don't break"`

### What you will see

```
Branch: main
Files to be staged and pushed (3):
----------------------------------------
  ?? notes.txt
  ?? app.py
  ?? README.md
----------------------------------------
Commit and push to origin/main? [Y/n]:
```

| You type         | Result                                                                    |
| :--------------- | :------------------------------------------------------------------------ |
| **Enter** or `y` | Commits and pushes. (When the default is `[Y/n]`, Enter means yes.)       |
| `n`              | Cancels. Nothing is committed or pushed.                                  |
| `a`              | Shows the full file list. Only offered when there are more than 10 files. |
| **Ctrl+C**       | Stops immediately.                                                        |

The letters beside each file are Git's status: `??` is a new file, `M` is changed, `D` is deleted.

---

## Warnings

lazypush colors files that need your attention.

### Red: RISKY PUSH DETECTED

These files look like passwords, keys or secrets. They are listed first, in red, and the warning appears at the top and again at the bottom of the list.

**The default flips to `[y/N]`, so pressing Enter cancels the push.** You have to type `y` on purpose.

What counts as risky:

| Type                                 | Examples                                                                                        |
| :----------------------------------- | :---------------------------------------------------------------------------------------------- |
| Keys and certificates                | `.pem` `.key` `.p12` `.pfx` `.jks` `.keystore` `.ppk` `id_rsa` `id_dsa` `id_ecdsa` `id_ed25519` |
| Passwords and tokens                 | `.env` `secret.` `secrets.` `secret_key` `credentials.` `api_key` `apikey` `service-account`    |
| Config files that often hold secrets | `.npmrc` `.pypirc` `.netrc` `.htpasswd` `.kdbx` `.tfstate` `.tfvars` `.aws/` `.ssh/`            |
| Folders that should never be pushed  | `node_modules/` `venv/` (also catches `.venv/`)                                                 |

Template files ending in `.example`, `.sample` or `.template` (like `.env.example`) are not flagged. Deleting a risky file is not flagged either.

**If a secret gets pushed, treat it as leaked and change it.** Deleting the file afterwards does not remove it from GitHub's history.

### Yellow: JUNK FILES DETECTED

These files usually do not belong in a repository. They are shown in yellow, and lazypush prints the exact lines to add to your `.gitignore`. The default stays `[Y/n]`, so this is only a nudge.

`.DS_Store` `Thumbs.db` `desktop.ini` `*.log` `*.tmp` `*.swp` `*.pyc` `__pycache__/` `.pytest_cache/` `*.sqlite` `*.sqlite3` `*.db` `build/` `dist/` `coverage/` `.idea/`

### Red: FILE TOO BIG FOR GITHUB

GitHub rejects any file over **100 MB**. If lazypush finds one, it shows the file name and size, then **stops before committing anything**. Remove the file or add it to `.gitignore`, then run lazypush again.

### Stopping files from showing up

Create a file named `.gitignore` in your project folder and list the names you want Git to skip, one per line:

```
.DS_Store
*.log
build/
```

Files that Git already tracks keep appearing until you stop tracking them. Run this once (it keeps the file on your disk):

```
git rm --cached <file>
```

---

## Setting up a new project

```
cd my-project
git init
git remote add origin https://github.com/YOUR-NAME/YOUR-REPO.git
lazypush first commit
```

Create the repository on GitHub **empty** (no README or license) so the first push is accepted.

---

## Something went wrong?

| Message                                     | What to do                                                                                                                                                                                                 |
| :------------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `'lazypush' is not recognized`              | Open a **new** terminal. Terminals that were open during install can't see the new PATH. If it still fails, run `install.bat` again.                                                                       |
| `Git is not installed.`                     | Install Git, then open a new terminal.                                                                                                                                                                     |
| `Not inside a Git repository.`              | Go to your project folder, or run `git init` there first.                                                                                                                                                  |
| `No 'origin' remote found.`                 | Run `git remote add origin <your-github-url>`.                                                                                                                                                             |
| `You are on a detached HEAD`                | Run `git checkout -b my-branch`. If you are in the middle of a rebase or merge, finish it first with `git rebase --continue` or cancel with `git rebase --abort`.                                          |
| `unresolved merge conflicts`                | Fix the conflicting files, then run lazypush again.                                                                                                                                                        |
| `Commit failed` / `Author identity unknown` | Run the two `git config --global` commands from [Before you start](#before-you-start).                                                                                                                     |
| `Push failed`                               | Your commit is saved locally. If someone else pushed first, run `git pull --rebase origin <branch>`, then `lazypush` again. If the pull shows conflicts, fix them and finish with `git rebase --continue`. |
| `Nothing new to commit`                     | Nothing changed. lazypush still pushes any commits that were never uploaded.                                                                                                                               |
| Windows or antivirus blocks `lazypush.exe`  | See [Security warnings](#security-warnings).                                                                                                                                                               |

### Made a mistake?

- **Committed, but not pushed yet:** `git reset --soft HEAD~1` undoes the commit and keeps your files.
- **Already pushed a secret:** change the secret first. Cleaning up GitHub's history is a separate, harder job.

---

## Limits

- Windows 10/11 64-bit only (other systems later).
- Pushes the **current branch** to **`origin`** only. There is no branch switching, merging or pulling.
- Never force-pushes.
- If the GitHub repository already has commits (for example, it was created with a README) and your local project is new, the first push is rejected. Run `git pull origin <branch> --allow-unrelated-histories` once, then use lazypush normally.
- If two people push to the same branch, pull first (see "Push failed" above).
- The risky-file list is a safety net, not a guarantee. A secret in a file with an unusual name will not be flagged. Keep your `.gitignore` up to date.

---

## Security warnings

`lazypush.exe` is not code-signed, so you may see:

- **SmartScreen** ("Windows protected your PC"): click **More info**, then **Run anyway**.
- **Antivirus false alarms:** programs packed with PyInstaller are sometimes flagged by mistake. The full source is in `lazypush.py`, and you can build the `.exe` yourself with the steps below.

---

## Build it yourself

You only need this to build from source. You need **64-bit Python 3.7 or newer** and Git.

**Run without building** (any system with Python):

```
python lazypush.py your message here
```

**Build the `.exe`** on Windows:

```
python -m pip install pyinstaller
python -m PyInstaller --onefile --name lazypush lazypush.py
```

- The result is `dist\lazypush.exe`.
- If `python` isn't recognized, use `py -m pip ...` and `py -m PyInstaller ...` instead.
- Write `PyInstaller` with capital P and I.
- Check you have 64-bit Python: `python -c "import struct; print(struct.calcsize('P')*8)"` should print `64`.

**Make a release zip:** put `lazypush.exe`, `install.bat` and `uninstall.bat` in one folder, zip it, and attach it to a GitHub Release.

---

## Files in this repository

```text
lazypush/
├── lazypush.py       # The program (source code)
├── install.bat       # Installer for Windows
├── uninstall.bat     # Uninstaller for Windows
└── README.md         # This file
```

The release zip contains `lazypush.exe`, `install.bat` and `uninstall.bat`.
