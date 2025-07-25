<div align="center">
    <picture>
        <source srcset="assets/logo/dark-mode/acubed.png"  media="(prefers-color-scheme: dark)">
        <img src="assets/logo/no-dark-mode/acubed.png" alt="Logo" width="200px" height=auto>
    </picture>
</div>

[![Release](https://img.shields.io/github/v/release/stepmanai/ACubed)](https://img.shields.io/github/v/release/stepmanai/ACubed)
[![Build status](https://img.shields.io/github/actions/workflow/status/stepmanai/ACubed/main.yml?branch=main)](https://github.com/stepmanai/ACubed/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/stepmanai/ACubed/branch/main/graph/badge.svg)](https://codecov.io/gh/stepmanai/ACubed)
[![Commit activity](https://img.shields.io/github/commit-activity/m/stepmanai/ACubed)](https://img.shields.io/github/commit-activity/m/stepmanai/ACubed)
[![License](https://img.shields.io/github/license/stepmanai/ACubed)](https://img.shields.io/github/license/stepmanai/ACubed)

A model training framework for building stepfile difficulty prediction models for open source rhythm games.

- **Github repository**: <https://github.com/stepmanai/ACubed/>
- **Documentation** <https://stepmanai.github.io/ACubed/>
- **Datasets**: <https://huggingface.co/datasets/stepmanai/ffr_charts>

## Prerequisites:

### System Requirements

This project is natively supported on **Ubuntu 22.04** (`ubuntu:jammy`) and later, in accordance with [Copier's installation requirements](https://github.com/copier-org/copier?tab=readme-ov-file#installation).

#### Windows Users

To run this project on Windows, install **Ubuntu 22.04** via the Microsoft Store after setting up **Windows Subsystem for Linux (WSL)**. Follow the official [WSL installation guide](https://learn.microsoft.com/en-us/windows/wsl/install) for step-by-step instructions.

> **Note**: These instructions assume you already have access to this repository. If not, please contact us to request access.

## Getting Started

> **Note**: These instructions assume you're setting up this workspace for the very first time. Feel free to skip any steps that are already complete in your environment.

Follow the steps below to set up your local development environment.

### 1. Clone the Repository

Clone this repository to your local machine and navigate into the project directory:

```bash
git clone https://github.com/stepmanai/ACubed.git
cd ACubed
```

### 2. Install System Dependencies

Install the required system packages:

> **Note**: You can skip any of these if they’re already installed.

```bash
sudo apt update
sudo apt install -y make python3-pip jq git-lfs
```

### 3. Install `uv`

Install [`uv`](https://github.com/astral-sh/uv) (a Python packaging tool):

```bash
wget -qO- https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### 4. Set Up Git LFS

Initialize and configure [Git Large File Storage (LFS)](https://git-lfs.com/):

```bash
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
git lfs install
```

### 5. Configure SSH for GitHub and Hugging Face

To securely interact with GitHub and Hugging Face using SSH:

1. **Generate a new SSH key (if needed):**

   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   cat ~/.ssh/id_ed25519.pub
   ```

2. **Add your SSH key to GitHub:**

   - Go to [GitHub SSH settings](https://github.com/settings/keys)
   - Click **New SSH key**, paste the contents of your `id_ed25519.pub` file, and save

3. **Add your SSH key to Hugging Face:**

   - Go to [Hugging Face SSH settings](https://huggingface.co/settings/ssh-keys)
   - Click **Add SSH key**, paste the same public key, and save

4. **Verify the connection:**

   ```bash
   ssh -T git@github.com
   ssh -T git@hf.co
   ```

> **Note**: Ensure your SSH key is loaded into the agent on each login, or use tools like `keychain` or `ssh-agent` configuration in `.bashrc`/`.zshrc`.

### 6. Set Up the Development Environment

Install Python dependencies and pre-commit hooks:

```bash
make install
```

### 7. Verify Pre-commit Hooks

Run the pre-commit hooks to ensure your environment is properly configured:

```bash
uv run pre-commit run -a
```

### 8. Launch Visual Studio Code

Open the project in VS Code:

```bash
code .
```

You are now ready to start development on your project!

Each time when code changes are made in the repository, run the pre-commit hooks to make sure that the build passes before opening a pull request, merging to main, or creating a new release. The project is designed so that the CI/CD pipeline will run these above code quality checks to enforce standardization.

To finalize the set-up for publishing to PyPI, see [here](https://fpgmaas.github.io/cookiecutter-uv/features/publishing/#set-up-for-pypi).
For activating the automatic documentation with MkDocs, see [here](https://fpgmaas.github.io/cookiecutter-uv/features/mkdocs/#enabling-the-documentation-on-github).
To enable the code coverage reports, see [here](https://fpgmaas.github.io/cookiecutter-uv/features/codecov/).

## Releasing a new version

- Create an API Token on [PyPI](https://pypi.org/).
- Add the API Token to your projects secrets with the name `PYPI_TOKEN` by visiting [this page](https://github.com/stepmanai/ACubed/settings/secrets/actions/new).
- Create a [new release](https://github.com/stepmanai/ACubed/releases/new) on Github.
- Create a new tag in the form `*.*.*`.

For more details, see [here](https://fpgmaas.github.io/cookiecutter-uv/features/cicd/#how-to-trigger-a-release).

---

Repository created by [stepmanai/project-bass](https://github.com/stepmanai/project-bass).

Repository structure based on [fpgmaas/cookiecutter-uv](https://github.com/fpgmaas/cookiecutter-uv).
