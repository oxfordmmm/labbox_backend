# Backend for LabBox

This is the backend for the LabBox application written using Python and FastAPI.

## Prerequisites

You will need to have an install of Python 3.12 or greater on you system. For
PostgreSQL you will version 15 or greater installed.

## Environment setup

After cloning the repo `cd` into the backend folder, create a virtual
environment and activate it.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Run pip to install the development dependencies

```bash
pip install -e .[dev]
```

Copy the `.env.example` file to `.env` and edit the `.env` file to include the
required settings got from your friendly administrator.

## Creating the database

Create a PostgreSQL database using your preferred method and add a user that has
permissions to create objects in this database. Note you will need to update the
`.env` file with the database connection information and user name.

## Updating the database

We use Alembic to handle the changes to the database (migrations), this is only
available when running in Development mode. Use the following command to update
the attached database to the latest version.

```bash
alembic upgrade head
```

If you have made changes to the database models, you will need to generate a new
migration using the following command.

```bash
alembic revision --autogenerate -m "message"
```

Replacing the message with something suitable. It is important to check the
migration that is generated, to make sure it is sensible. Migrations are stored
in the `migrations/versions` folder.

Please note when running migrations the `__dbrevision__` variable in
`src\app\__init__.py` will be updated to the new head revision. Please remember
to commit this file in addition to your migration files.

## Running the backend

You can then run the backend using the following command or use the debugger in
VS Code, which should be setup as "Run Uvicorn Directly". Running using the
VSCode setup will run with increased logging level "Trace".

```bash
PYTHONPATH=$PWD/src python3 ./src/app/main.py
```

Please note running using the above command will run with production settings
from `main.py`.

Please note the backend is set up to run under port 8000. If this port is in use
on your system you will need to modify the `.env` file in the backend and the
server:proxy:target setting in the `vite.config.ts` file in the frontend.

## .env file

The `.env` file contains the secrets for the application, including Auth0 and
database connection information. Do not copy this file to GitHub or anywhere
else public. A template `.env.example` is provided as a base to create the
`.env` file on your local machine.

## Running in docker

A `Dockerfile` is provided to build a container, and also used by the GitHub
actions to build the container and deploy to ghcr.io.

If you are running the database on your local machine, you are not able to use
`localhost` or `127.0.0.1` for the `DATABASE_HOST` entry in the `.env` file.
Instead use `host.docker.internal` for the `DATABASE_HOST` entry in your `.env`
file. If you also want the `.env` file to work when running locally, not in a
docker container, you will need to edit your `hosts` file to point
`host.docker.internal` at your local machine.

NOTE: `host.docker.internal` works for docker running on Mac and Windows at
version 20.10 and above. But to get this to work on Linux will need to add
`--add-host=host.docker.internal:host-gateway` to your `docker` command to
enable the feature.

To build the container locally for testing use a command similar to the
following

```shell
docker build -t labbox_backend .
```

When testing the docker container with the front-end container use the following
command to run the back-end container.

```shell
docker run --env-file ./.env -p 8000:8000 --network labbox_network --name labbox_backend -d labbox_backend
```

The `-p` is not needed for the containers to communicate, but is useful in
development to test the API. The `--network` and `--name` are needed for the
containers to communicate.

## Debugging into Docker

A `docker-compose.debug.yml` file is provided to allow the running of the
back-end in a docker container and allow debugging. In VSCode this can be
right-clicked and `compose up` command chosen. A VSCode debugger profile is
provided "Python: Remote Attach" to attach to the docker container.
