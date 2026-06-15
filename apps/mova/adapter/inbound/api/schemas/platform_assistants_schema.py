from pydantic import BaseModel, Field


class PlatformAssistantsSchema(BaseModel):

    id: int = Field(0, description="Assistants ID")
    name: str = Field("AI ì»¨ì‹œ?´ì? (AI Concierge)", description="AI Concierge's name")
    # ê·¹ì¥ ?…êµ¬?ì„œ ê´€ê°ì„ ë§ì´?˜ëŠ” AI ?ë‹´?? assistants ?Œì´ë¸?ê´€ë¦?
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "AI ì»¨ì‹œ?´ì? (AI Concierge)",
            }
        }
    }
