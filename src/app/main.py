import logging
from os import cpu_count
from pathlib import Path
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import app_config
from app.db import run_alembic_upgrade_to_head
from app.logs import add_json_handler
from app.routes.mutation_routes import router as mutation_router
from app.routes.schema_routes import router as schema_router
from app.routes.spreadsheet_routes import router as spreadsheet_router
from app.routes.summary_routes import router as summary_router
from app.utils.auth import auth

app = FastAPI()

origins = [
    "https://labbox.ouh.mmmoxford.uk:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(add_json_handler)

app.include_router(spreadsheet_router, prefix="/spreadsheet", tags=["spreadsheet"])
app.include_router(summary_router, prefix="/summary", tags=["summary"])
app.include_router(mutation_router, prefix="/mutation", tags=["mutation"])
app.include_router(schema_router, prefix="/schema", tags=["schema"])


@app.get("/public")
def public() -> dict:
    """Test endpoint that requires no authentication

    Returns:
        dict: A success message dict
    """
    result = {
        "status": "success",
        "msg": (
            "Hello from a public endpoint! You don't need to be "
            "authenticated to see this."
        ),
    }
    return result


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    """Returns the favicon.ico file

    Returns:
        FileResponse: The favicon.ico file
    """
    current_file_path = Path(__file__).resolve()
    favicon_path = (
        current_file_path.parent / "assets" / "images" / "favicon" / "favicon.ico"
    )
    return FileResponse(str(favicon_path))


@app.get("/private")
async def private(auth_result: Dict[str, Any] = Security(auth.verify)) -> Dict[str, Any]:
    """Protected test end point that requires authentication

    Args:
        auth_result (str, optional): _description_. Defaults to Security(auth.verify).

    Returns:
        dict: _description_
    """
    return auth_result


@app.get("/private-scoped")
def private_scoped(
    auth_result: Dict[str, Any] = Security(auth.verify, scopes=["admin"]),
) -> Dict[str, Any]:
    """A protected endpoint that requires a valid token with the 'admin' scope

    Args:
        auth_result (str, optional): Defaults to Security(auth.verify, scopes=["admin"]).

    Returns:
        str: A success message
    """
    return auth_result


def get_cpu_limit() -> int:
    """Find the number of CPUs that this can use. Accounts for containers showing node CPUs.

    Returns:
        int: Number of CPUs to use
    """
    try:
        with Path.open(Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us"), "r") as fp:
            cfs_quota_us = int(fp.read())
        with Path.open(Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us"), "r") as fp:
            cfs_period_us = int(fp.read())
        container_cpus = cfs_quota_us // cfs_period_us
        # For physical machine, the `cfs_quota_us` could be '-1'
        cpus = cpu_count() if container_cpus < 1 else container_cpus
    except FileNotFoundError:
        # These files don't exist on local machines, so fallback to cpu_count
        cpus = cpu_count()
    if cpus is None:
        # Unknown value given by OS so fallback to 2
        cpus = 2
    return cpus


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Run Alembic migrations before starting the server
    try:
        run_alembic_upgrade_to_head()
    except Exception:
        logging.error(
            "Failed to complete database migrations. Application will not start."
        )
        exit(1)

    worker_count = get_cpu_limit()
    if worker_count is not None:
        worker_count = worker_count * 2 + 1

    uvicorn.run(
        "main:app",
        host=app_config.HOST,
        port=int(app_config.PORT),
        log_level="info",
        workers=worker_count,
    )
