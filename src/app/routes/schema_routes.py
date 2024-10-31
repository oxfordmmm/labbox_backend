import asyncio
from typing import Any, Dict, List

from app.db import get_session
from app.utils.auth import auth
from fastapi import APIRouter, Security
from sqlalchemy.sql.expression import func

router = APIRouter()

type_mapping = {
    "integer": "integer",
    "character varying": "string",
    "double": "number",
    "boolean": "boolean",
    "date": "date",
    "text": "string",
}

allowed_view_names = [
    "flattened_others_view",
    "flattened_sample_details_view",
    "flattened_specimen_details_view",
    "runs_view",
    "samples_view",
    "specimens_view",
    "storages_view",
]


async def get_view_columns(view_name: str) -> List[Dict[str, Any]]:
    async with get_session() as session:
        rows = await session.execute(func.public.get_view_columns(view_name))
    columns = [dict(row) for row in rows]
    return [
        {
            key: type_mapping.get(
                value,
                next(
                    (v for k, v in type_mapping.items() if value.startswith(k)),
                    value,
                ),
            )
            for key, value in column.items()
        }
        for column in columns
    ]


async def get_view_schema(view_name: str) -> Dict[str, Any]:
    columns = await get_view_columns(view_name)
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            column_name: {"type": "string", "format": "date"}
            if data_type == "date"
            else {"type": data_type}
            for column in columns
            for column_name, data_type in column.items()
        },
    }
    return schema


@router.get("/{view_name}")
async def get_schema(
    view_name: str,
    auth_result: Dict[str, Any] = Security(auth.verify),
):
    if view_name not in allowed_view_names:
        return {"error": "Invalid view name"}
    return await get_view_schema(view_name)


# for testing
if __name__ == "__main__":
    data = asyncio.run(get_view_schema("samples_view"))
    print(data)
