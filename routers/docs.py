from fastapi import APIRouter, Request
from fastapi.openapi.docs import get_swagger_ui_html

router = APIRouter()

@router.get("/docs", include_in_schema=False)
async def get_docs(
    request: Request
):
    return get_swagger_ui_html(
        openapi_url=request.scope.get("root_path") + "/openapi.json",
        title="Swagger"
    )