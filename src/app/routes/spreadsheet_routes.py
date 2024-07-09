import json

from app.db import get_session
from app.importers.import_spreadsheet import import_data
from app.utils.auth import auth
from fastapi import APIRouter, Form, Request, Security
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/upload")
async def upload(
    request: Request,
    Runs: str = Form(...),
    Specimens: str = Form(...),
    Samples: str = Form(...),
    Storage: str = Form(...),
    dryRun: bool = Form(False),
    auth_result: str = Security(auth.verify),
):
    runs = json.loads(Runs)
    specimens = json.loads(Specimens)
    samples = json.loads(Samples)
    storage = json.loads(Storage)
    logger = request.state.logger

    async with get_session() as session:
        await import_data(
            session=session,
            Runs=runs,
            Specimens=specimens,
            Samples=samples,
            Storage=storage,
            dryrun=dryRun,
            logger=logger,
        )

    logs = [
        {"id": i + 1, "level": log["levelname"], "msg": log["msg"]}
        for i, log in enumerate(logger.get_logs())
    ]

    msg = (
        "Excel uploaded failed"
        if logger.error_occurred
        else "Excel uploaded successfully" + (" (dry run)" if dryRun else "")
    )

    return JSONResponse(
        status_code=200,
        content={"msg": msg, "logs": logs},
    )
