# lab-flask-rest

[![Build Status](https://github.com/nyu-devops/lab-flask-rest/actions/workflows/workflow.yaml/badge.svg)](https://github.com/nyu-devops/lab-flask-rest/actions)

NYU DevOps lab showing a best practice REST API complete with unit tests.

## Introduction

This lab demonstrates how to create a simple REST service using Python Flask and SQLite.
The resource model is persistenced using SQLAlchemy to keep the application simple. SQLAlchemy is an Object Relational Mapper (ORM) that will allow you to work with classes instead of database records.

This projects purpose is to show the correct API and return codes that should be used for a REST API. Everything is contained ina single

## Prerequisite Installation for Intel Mac & PC

The easiest way to use this lab is with **Vagrant** and **VirtualBox**. if you don't have this software the first step is down download and install it.

Download [VirtualBox](https://www.virtualbox.org/)

Download [Vagrant](https://www.vagrantup.com/)

Then all you have to do is clone this repo and invoke vagrant:

```bash
    git clone https://github.com/nyu-devops/lab-flask-rest.git
    cd lab-flask-rest
    vagrant up
    vagrant ssh
    cd /vagrant
    FLASK_APP=service:app flask run -h 0.0.0.0
```

You can also automatically set the environment variable FLASK_APP using a `.env` file.
There is an example in this repo called `dot-env-example` that you can simply copy.

```sh
    cp dot-env-example .env
```

The `.env` file will be loaded when you do `flask run` so that you don't have to specify
any environment variables.

## Alternate for M1 Macs using Vagrant and Docker

You can also use [Docker Desktop for Apple Silicon](https://docs.docker.com/docker-for-mac/apple-silicon/) as a provider instead of VirtualBox. This is useful for owners of Apple M1 Silicon Macs which cannot run VirtualBox because they have a CPU based on ARM architecture instead of Intel.

Just add `--provider docker` to the `vagrant up` command like this:

```sh
vagrant up --provider docker
```

This will use a Docker container instead of a Virtual Machine (VM). Of course Intel Macs and Windows PCs can use this as well. Just install the appropreate Docker Desktopo build.

## Alternate install using VSCode and Docker

You can also develop in Docker containers using VSCode. This project contains a `.devcontainer` folder that will set up a Docker environment in VSCode for you. You will need the following:

- Docker Desktop for [Mac](https://docs.docker.com/docker-for-mac/install/) or [Windows](https://docs.docker.com/docker-for-windows/install/)
- Microsoft Visual Studio Code ([VSCode](https://code.visualstudio.com/download))
- [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) VSCode Extension

It is a good idea to add VSCode to your path so that you can invoke it from the command line. To do this, open VSCode and type `Shift+Command+P` on Mac or `Shift+Ctrl+P` on Windows to open the command palete and then search for "shell" and select the option **Shell Command: Install 'code' command in Path**. This will install VSCode in your path.

Then you can start your development environment up with:

```bash
    git clone https://github.com/nyu-devops/lab-flask-rest.git
    cd lab-flask-rest
    code .
```

The first time it will build the Docker image but after that it will just create a container and place you inside of it in your `/workspace` folder which actually contains the repo shared from your computer. It will also install all of the VSCode extensions needed for Python development.

If it does not automatically pronot you to open the project in a container, you can select the green icon at the bottom left of your VSCode UI and select: **Remote Containers: Reopen in Container**.

## Alternate manual install using local Python

If you have Python 3 installed on your computer you can make a virtual environment and run the code locally with:

```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    FLASK_APP=service:app flask run
```

You will also need Docker on your computer to run a container for the database.

## Manually running the Tests

Run the tests using `nosetests`

```bash
  $ nosetests --with-spec --spec-color
```

**Notes:** the parameter flags `--with-spec --spec-color` add color so that red-green-refactor is meaningful. If you are in a command shell that supports colors, passing tests will be green while failing tests will be red. The flag `--with-coverage` is automatcially specified in the `setup.cfg` file so that code coverage is included in the tests.

The Code Coverage tool runs with `nosetests` so to see how well your test cases exercise your code just run the report:

```bash
  $ coverage report -m
```

This is particularly useful because it reports the line numbers for the code that is not covered so that you can write more test cases.

To run the service use `flask run` (Press Ctrl+C to exit):

```bash
  $ FLASK_APP=service:app flask run -h 0.0.0.0
```

You must pass the parameters `-h 0.0.0.0` to have it listed on all network adapters to that the post can be forwarded by `vagrant` to your host computer so that you can open the web page in a local browser at: http://localhost:5000

## Vagrant shutdown

If you are using Vagrant and VirtualBox, when you are done, you should exit the virtual machine and shut down the vm with:

```bash
 $ exit
 $ vagrant halt
```

If the VM is no longer needed you can remove it with:

```bash
  $ vagrant destroy
```

This repo is part of the DevOps course CSCI-GA.2820-001/002 at NYU taught by John Rofrano.
