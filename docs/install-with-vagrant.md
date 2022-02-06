# Install Prerequisites using Vagrant

The class is taught using **Docker** and **Visual Studio Code** with the **Remote Containers** extension and it is recommended that you use this combination if you can. If, for some reason you cannot or do not want to use it, you can create your development environment for this lab using **Vagrant** in combination with **VirtualBox** or **Docker**.

## Software Installation

If you don't have this software the first step is down download and install it. Everyone will need Vagrant.

- Download [Vagrant](https://www.vagrantup.com/)

If you have an Apple M1 Silicon Mac you cannot use VirtualBox so you must download Docker instead.

- Download [Docker Desktop](https://www.docker.com/products/docker-desktop)

If you have an Intel Mac or an Intel Windows PC, you can use VirtualBox but you can also use Docker if you wish.

- Download [VirtualBox](https://www.virtualbox.org/)

If you don't want to manually install these you can use Homebrew or Chocolatey.

### Homebrew commands

Install Git, Vagrant, and Visual Studio Code as a base:

```bash
brew install git
brew install --cask vagrant
brew install --cask visual-studio-code
```

Apple M1 Silicon use Docker

```bash
brew install --cask docker
```

All others can use Virtualbox (or Docker)

```bash
brew install --cask virtualbox
```

### Chocolatey commands

Install Git, Vagrant, and Visual Studio Code as a base:

```bash
choco install git
choco install vagrant
choco install vscode
```

Apple M1 Silicon use Docker

```bash
choco install docker-desktop
```

All others can use Virtualbox (or Docker)

```bash
choco install virtualbox
```

## Bringing up the development environment

Once all of the prerequisite software is installed, you must clone this repo and invoke vagrant.

1. Clone the repo and `cd` into the folder

```bash
git clone https://github.com/nyu-devops/lab-flask-rest.git
cd lab-flask-rest
```

2. Bring up Vagrant using either VirtualBox or Docker

If you are using **VirtualBox** use this command to bring up the environment:

```bash
vagrant up
```

If you are using **Docker** use this command to bring up the environment:

```bash
vagrant up --provider docker
```

*Note: if you did not install VirtualBox then you can also just use `vagrant up` to bring up Vagrant using Docker. The only time you need to use `--provider docker` is if you have both Docker and VirtualBox installed so that Vagrant knows which one you want to use.*

3. Finally to get inside of the Virtual Machine (VM) in either environment use:

```bash
vagrant ssh
```

Once inside the VM, you can run the code by switching into the `/vagrant` folder and running `flask`.

```bash
cd /vagrant
flask run -h 0.0.0.0
```

You should now have a fully operational development environment to work in.

## Shutdown the development environment

When you are done with the lab, you should exit the virtual machine and shut down the vm with:

```bash
 exit
 vagrant halt
```

If the VM is no longer needed you can remove it with:

```bash
  vagrant destroy
```
