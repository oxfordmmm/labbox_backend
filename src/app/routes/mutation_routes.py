import json
from typing import Any, Dict

from app.db import get_session
from app.importers.import_gpas import import_mutation
from app.utils.auth import auth
from fastapi import APIRouter, Form, Request, Security
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/upload")
async def upload(
    request: Request,
    Mutation: str = Form(...),
    Mapping: str = Form(...),
    dryRun: bool = Form(False),
    auth_result: Dict[str, Any] = Security(auth.verify),
):
    mutation = json.loads(Mutation)
    mapping = json.loads(Mapping)
    logger = request.state.logger

    async with get_session() as session:
        await import_mutation(
            session=session,
            Mutation=mutation,
            Mapping=mapping,
            logger=logger,
            dryrun=dryRun,
        )

    logs = [
        {"id": i + 1, "level": log["levelname"], "msg": log["msg"]}
        for i, log in enumerate(logger.get_logs())
    ]
    print(f"logs: {logs}")

    msg = (
        "Mutation uploaded failed"
        if logger.error_occurred
        else "Mutation uploaded successfully" + (" (dry run)" if dryRun else "")
    )

    return JSONResponse(
        status_code=200,
        content={"msg": msg, "logs": logs},
    )
