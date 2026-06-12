from pydantic import BaseModel, Field


class MessageSchema(BaseModel):
    role: str
    content: str


class ChatSchema(BaseModel):
    messages: list[MessageSchema] = Field(..., description="대화 이력 (role: user|assistant)")
    systemInstruction: str | None = Field(None, description="선장 역할 시스템 프롬프트")
    model: str | None = Field("flash", description="Gemini 모델 키")

class SmithCaptainSchema(BaseModel):

    id: int = Field(0, description="Captain ID")
    name: str = Field("에드워드 스미스", description="Captain's name")
    # 타이타닉 선장. 백만장자들의 선장이라 불렸으며 고조되는 위기 속에 배와 운명을 함께함

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 4,
                "name": "Edward Smith",
            }
        }
    }



    