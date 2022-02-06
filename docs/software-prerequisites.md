# Prerequisite Installation for the lab

This lab uses **Docker** and **Visual Studio Code** with the **Remote Containers** extension to provide a consistent repeatable disposable development environment for all of the labs in this course.

You will need the following software installed:

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Microsoft [Visual Studio Code](https://code.visualstudio.com)
- [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension from the Visual Studio Marketplace

## Install the required software

All of these can be installed manually by clicking on the links above or you can use a package manager like **Homebrew** on Mac of **Chocolatey** on Windows. If you want to use one of these package managers, follow these instructions:

- [Install using Homebrew](install-with-homebrew.md)
- [Install using Chocolatey](install-with-choco.md)

Alternately you can use Vagrant to bring up a virtual machine to work in following these instructions but this is no longer the recommended way to work. Only use if you cannot use the above two methods: [Install with Vagrant](install-with-vagrant.md)

## Some Docker commands for manual control

If you want to manually close the containers you can use the command pallet and select **Close Remote Connection**. If you want to permanently delete the container you can use Docker commands to:

```bash
docker ps -a
docker stop <container-id>
docker rm <container-id>
```

Where `<container-id>` is the id of the container returned from the `docker ps -a` command.

For Example:

```bash
$ docker ps -a
                                                                                                  (master)
CONTAINER ID   IMAGE                                              COMMAND                  CREATED          STATUS          PORTS      NAMES
d9c94acd264b   vsc-lab-starter-2013d33dfd4af07fa71a13e87cbc6b63   "/bin/sh -c 'echo Co…"   56 minutes ago   Up 56 minutes   5000/tcp   affectionate_elgamal

$ docker stop d9c94acd264b
$ docker rm d9c94acd264b
```
