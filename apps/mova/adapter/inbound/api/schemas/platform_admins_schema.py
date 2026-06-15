from pydantic import BaseModel, Field


class PlatformAdminsSchema(BaseModel):

    id: int = Field(0, description="Admins ID")
    name: str = Field("총�?배인 (Executive)", description="Executive's name")
    # 극장 ?�체�?관리하??최고 책임?? admins ?�이�?관�?
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "총�?배인 (Executive)",
            }
        }
    }
