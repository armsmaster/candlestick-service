from pydantic import BaseModel, ConfigDict


class HTTPErrorSchema(BaseModel):
    """HttpError Schema."""

    detail: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"detail": "HTTPException raised."},
        }
    )
