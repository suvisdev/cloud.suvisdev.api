from dataclasses import dataclass, field


@dataclass
class ChatIntentDto:
    refined_query: str = ""
    keywords: list[str] = field(default_factory=list)
    intent_type: str = "mood"
    search_filters: dict = field(default_factory=dict)
