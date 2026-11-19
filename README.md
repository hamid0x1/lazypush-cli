⚡ lazypush

> Stage, commit, and push your active Git branch in a single command. Zero dependencies.

## lazypush is a lightweight, zero-dependency Python CLI tool that collapses the repetitive `git add .`, `git commit`, and `git push` cycle into one fast terminal command. It automatically detects whichever branch you are currently working on (`main`, `dev`, feature branches) and sets up remote tracking on your first push.

✨ Features
One-Command Workflow: Replaces three separate Git commands with a single `lazypush` call.
Branch-Aware: Never hardcodes `main`. Automatically detects your active branch (`main`, `master`, `dev`, `feature/xyz`).
Smart Upstream Linking: Automatically runs `git push -u origin <branch>` the first time you push a new local branch.
No Quotes Needed: Type your commit message naturally right after the command (`lazypush fixed login bug`).
Interactive Fallback: Run `lazypush` with no arguments to be prompted for your commit message.
Zero Dependencies: Uses only Python's built-in standard library (`subprocess`, `sys`)—no `pip install` required.

---

📋 Prerequisites
Python 3.7+
Git (installed and available in your system `PATH`)

---

🚀 Installation
Linux & macOS
Clone the repository:

```bash
   git clone https://github.com/<your-username>/lazypush.git
   cd lazypush
```

Move the script to your local `bin` folder and make it executable:

```bash
   mkdir -p ~/.local/bin
   cp lazypush.py ~/.local/bin/lazypush
   chmod +x ~/.local/bin/lazypush
```

Make sure `~/.local/bin` is in your `PATH` (add this to `~/.bashrc` or `~/.zshrc` if needed):

```bash
   export PATH="$HOME/.local/bin:$PATH"
```

---

Windows (10 / 11)
Clone or download this repository into a permanent folder (for example, `C:\Users\<YourUsername>\lazypush`).
Create a file named `lazypush.bat` inside that same folder with the following content:

```bat
   @echo off
   python "%~dp0lazypush.py" %*
```

Add that folder to your User `PATH`:
Press Win + S and open "Edit environment variables for your account".
Under User variables, select Path → click Edit → New.
Paste `C:\Users\<YourUsername>\lazypush` and click OK.
Restart your terminal.

---

💻 Usage
Navigate into any existing Git repository and run:
Inline Commit Message (Fastest)

```bash
lazypush updated navbar alignment
```

Equivalent to running:

```bash
git add .
git commit -m "updated navbar alignment"
git push origin <current-branch>
```

Interactive Mode

```bash
lazypush
# Prompts: Commit message:
```

---

⚠️ Important Notes
`git add .` Behavior: `lazypush` stages all modified and untracked files in your current directory. Make sure your `.gitignore` is properly configured so you don't accidentally push `.env` files, secrets, or build folders (`node_modules/`, `__pycache__/`, etc.).
Existing Repos Only: Your folder must already be initialized as a Git repository with an `origin` remote configured.

---

🤝 Contributing
Contributions, bug reports, and feature ideas are welcome!
Fork the repository.
Create a new feature branch (`git checkout -b feature/your-idea`).
Commit and push your changes (`lazypush added your idea`).
Open a Pull Request against `main`.

---

📄 License
Distributed under the MIT License. See `LICENSE` for more information.
