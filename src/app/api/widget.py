from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
 
from app.api.auth.deps import DbSession
from app.db.models import Conversation, Message, MessageRole, Site
from app.schemas.widget import WidgetMessageIn, WidgetMessageOut
from app.services.ai.rag import answer_question
 
router = APIRouter(prefix="/widget", tags=["Widget"])


@router.post("/message", response_model=WidgetMessageOut)
async def sent_widget_message(payload: WidgetMessageIn, db: DbSession):
    site = await db.get(Site, payload.site_id)
    if site is None or not site.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Сайт не найден или отключён")

    result = await db.execute(
        select(Conversation).where(
            Conversation.site_id == site.id,
            Conversation.session_id == payload.session_id,
        )
    )
    conversation = result.scalar_one_or_none()

    if conversation is None:
        conversation = Conversation(
            site_id=site.id,
            session_id=payload.session_id,
            visitor_id=payload.visitor_id,
            first_page_url=payload.current_page_url,
            current_page_url=payload.current_page_url,
            referrer=payload.referrer,
        )
        db.add(conversation)
    else:
        conversation.current_page_url = payload.current_page_url

    await db.commit()
    await db.refresh(conversation)

    db.add(Message(conversation_id=conversation.id, role=MessageRole.user, content=payload.message))
    await db.commit()

    rag_result = await answer_question(db, site.id, payload.message)
 
    db.add(
        Message(
            conversation_id=conversation.id,
            role=MessageRole.assistant,
            content=rag_result["answer"],
            sources=rag_result["sources"],
        )
    )
    await db.commit()
 
    return WidgetMessageOut(
        conversation_id=conversation.id,
        answer=rag_result["answer"],
        sources=rag_result["sources"],
    )

