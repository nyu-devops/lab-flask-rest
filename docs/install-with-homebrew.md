# Install Prerequisites on macOS using Homebrew

If you are using a Mac it is strongly suggested that you use `homebrew` to manage all of your development tools. If you don't have homebrew you can install it from [brew.sh](http://brew.sh) or just open a `terminal` and use this command:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Once installed you can install all of the prerequisite software for the labs using these commands:

```bash
xcode-select --install
```

This will install prerequisites for `git`. Then install the tools with:

```bash
brew install git
brew install --cask docker
brew install --cask visual-studio-code
```

You must setup Visual Studio Code as a Mac to launch from the command line using these [instructions](https://code.visualstudio.com/docs/setup/mac#_launching-from-the-command-line). Then you can run the `code` command to install the remote containers extension.

```bash
code --install-extension ms-vscode-remote.remote-containers
```

It is a good idea to add VSCode to your path so that you can invoke it from the command line. To do this, open VSCode and type `Shift+Command+P` on Mac to open the command palette and then search for "*shell*" and select the option **Shell Command: Install 'code' command in Path**. This will install VSCode in your path.

That's it! You can now [bring up the development environment](../README.md#bring-up-the-development-environment)
