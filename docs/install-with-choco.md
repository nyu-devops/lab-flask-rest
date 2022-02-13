# Install Prerequisites on Windows using Chocolatey

If you are using a Windows it is strongly suggested that you use `choco` to manage all of your development tools. If you don't have Chocolatey you can find instructions to install it from [chocolatey.org](https://docs.chocolatey.org/en-us/choco/setup)

Open a **Command Prompt** (`cmd`) and then:

```cmd
@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
```

If you are using **Windows Home Edition** you must install *Windows Subsystem for Linux* version 2 (WSL2) first. Please follow these instructions on [How to Install WSL 2 on Windows Home](https://evidencen.com/wsl2/). Once that is complete you can continue with these instructions.

After Chocolatey is installed, you can install all of the prerequisite software for the labs using these commands:

```bash
choco install git
choco install docker-desktop
choco install vscode
code --install-extension ms-vscode-remote.remote-containers
```

That's it! You can now [bring up the development environment](../README.md#bring-up-the-development-environment)
