# lab-flask-rest

[![language](https://img.shields.io/badge/Language-Python-blue.svg)](http://python.org)
[![Build Status](https://github.com/nyu-devops/lab-flask-rest/actions/workflows/ci.yaml/badge.svg)](https://github.com/nyu-devops/lab-flask-rest/actions)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**NYU DevOps and Agile Methodologies** lab showing a best practice for creating REST API, complete with unit tests.

## Introduction

This lab demonstrates how to create a simple RESTful service using **Python Flask** and **Redis**. It does not use any other frameworks because it is intended to show how to build a REST API manually following good RESTful practices.

The data is persisted using Redis to keep the application simple. Redis was chosen because the application keeps track of counters and their values and Redis is a memcached database that is perfect for persisting key/value pairs. Using a relational database like PostgreSQL or MySQL, or using a NoSQL document database like MongoDB or CouchDB would have been overkill.

This project's purpose is to show how to construct the proper endpoints and return codes that should be used to make a service RESTful. Everything is contained in a single `app.py` module for simplicity. Future labs will build more complex services in Python packages. For now, just *bask in the mindfulness of app.py's simplicity*.

## Software prerequisites

Check to make sure that you have the [Prerequisite software installed](docs/software-prerequisites.md) before starting this lab. Then all you need to do is:

## Bring up the development environment

To bring up the development environment you should clone this repo, change into the repo directory, and then open Visual Studio Code using the `code .` command. VS Code will prompt you to reopen in a container and you should say **select** it. This will take a while the first time as it builds the Docker image and creates a container from it to develop in.

```bash
git clone https://github.com/nyu-devops/lab-flask-rest.git
cd lab-flask-rest
code .
```

Note that there is a period `.` after the `code` command. This tells Visual Studio Code to open the editor and load the current folder of files.

The first time it will build the Docker image but after that it will just create a container and place you inside of it in your `/app` folder which actually contains the repo shared from your computer. It will also install all of the Visual Studio Code extensions needed for Python development.

If it does not automatically prompt you to open the project in a container, you can select the green icon at the bottom left of your Visual Studio Code UI and select: **Remote Containers: Reopen in Container**.

Once the environment is loaded you should be placed at a `bash` prompt in the `/app` folder inside of the development container. This folder is mounted to the current working directory of your repository on your computer. This means that any file you edit while inside of the `/app` folder in the container is actually being edited on your computer. You can then commit your changes to `git` from either inside or outside of the container.

## Make sure it all works

While this lab is not about testing, it is always a good idea to include tests with any code that you write. The first thing you want to do is run the tests to make sure that your environment is working correctly. Then run the code.

### Run the test suite

Run the tests in a `bash` terminal using the following command:

```bash
nosetests
```

This will run the test suite and report your code coverage. If you are interested, the tests are in the `./tests` folder and their configuration is controlled by the `setup.cfg` and `.coveragerc` files. The code coverage is particularly useful because it reports the line numbers for the code that is not covered so that you can write more test cases.

### Run the REST service

To run the service, use the same `bash` terminal that you ran the tests in and use `flask run` (Press Ctrl+C to exit):

```bash
flask run -h 0.0.0.0 -p 8000
```

You must pass the parameters `-h 0.0.0.0` to have it listed on all network adapters so that the nextwork port `8000` can be forwarded by `docker` to your host computer so that you can open the web page in a local browser at: http://localhost:8000

That's it! You should have a fully functioning REST API.

## Make some REST calls

With the service running, open a second `bash` terminal and issue the following `curl` commands:

List all counters:

```bash
curl -i -X GET http://127.0.0.1:8000/counters
```

Create a counter:

```bash
curl -i -X POST http://127.0.0.1:8000/counters/foo
```

Read a counter:

```bash
curl -i -X GET http://127.0.0.1:8000/counters/foo
```

Update a counter:

```bash
curl -i -X PUT http://127.0.0.1:8000/counters/foo
```

Delete a counter:

```bash
curl -i -X DELETE http://127.0.0.1:8000/counters/foo
```

Reset action on a counter:

```bash
curl -i -X PUT http://127.0.0.1:8000/counters/foo/reset
```

You can also experiment with a REST client like [Postman](https://www.postman.com). This makes it much easier to manipulate your REST API than using the command line.

## Bring down the development environment

There is no need to manually bring the development environment down. When you close Visual Studio Code it will wait a while to see if you load it back up and if you don't it will stop the Docker containers. When you come back again, it will start them up and resume where you left off.

If you have any issues with the Docker containers, here are some tips for [manually controlling containers](docs/software-prerequisites.md#some-docker-commands-for-manual-control)

## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repo is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created by *John Rofrano*
