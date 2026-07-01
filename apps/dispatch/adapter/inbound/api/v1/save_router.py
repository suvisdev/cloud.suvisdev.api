from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response

from dispatch.adapter.inbound.api.schemas.inbox_schema import InboxItemSchema, InboxReceiveSchema
from dispatch.app.dtos.inbox_dto import InboxSaveCommand
from dispatch.app.ports.input.inbox_use_case import InboxUseCase
from dispatch.dependencies.inbox_provider import get_inbox_use_case

inbox_router = APIRouter(prefix="/inbox", tags=["dispatch-inbox"])


@inbox_router.post("", response_model=InboxItemSchema)
async def receive_inbox(
    req: InboxReceiveSchema,
    use_case: InboxUseCase = Depends(get_inbox_use_case),
) -> InboxItemSchema:
    item = await use_case.save(
        InboxSaveCommand(sender=req.sender, subject=req.subject, body=req.body)
    )
    return InboxItemSchema(
        id=item.id,
        sender=item.sender,
        subject=item.subject,
        body=item.body,
        received_at=item.received_at,
    )


@inbox_router.get("", response_model=list[InboxItemSchema])
async def list_inbox(
    limit: int = Query(default=50, le=200),
    use_case: InboxUseCase = Depends(get_inbox_use_case),
) -> list[InboxItemSchema]:
    items = await use_case.list_all(limit)
    return [
        InboxItemSchema(
            id=i.id, sender=i.sender, subject=i.subject, body=i.body, received_at=i.received_at
        )
        for i in items
    ]


@inbox_router.delete("/{item_id}", status_code=204)
async def delete_inbox(
    item_id: int,
    use_case: InboxUseCase = Depends(get_inbox_use_case),
) -> Response:
    await use_case.delete(item_id)
    return Response(status_code=204)
