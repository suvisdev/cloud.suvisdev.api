from pydantic import BaseModel, Field


class PlatformUsersSchema(BaseModel):

    id: int = Field(0, description="Users ID")
    name: str = Field("ê´€ê°?(Audience)", description="Audience's name")
    # ?œë¹„?¤ë? ?´ìš©?˜ëŠ” ?¼ë°˜ ?¬ìš©?ì´??ëª¨ë“  Mova ?°ì´?°ì˜ ?¤ì§ˆ??ì£¼ì²´. users ?Œì´ë¸?ê´€ë¦?
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "ê´€ê°?(Audience)",
            }
        }
    }
