# Backend for LabBox

This is the backend for the LabBox application written using Python and FastAPI.

## Prerequisites

You will need to have an install of Python 3.12 or greater on you system.

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
VS Code, which should be setup

```bash
python3 ./src/app/main.py
```

Please note the backend is set up to run under port 8000. If this port is in use
on your system you will need to modify the `.env` file in the backend and the
server:proxy:target setting in the `vite.config.ts` file in the frontend.