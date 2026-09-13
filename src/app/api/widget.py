import uuid

from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select
from pydantic import BaseModel
 
from app.api.auth.deps import DbSession
from app.db.models import Conversation, Message, MessageRole, Site, Lead
from app.db.models.client import Client
from app.schemas.widget import LeadIn, WidgetMessageIn, WidgetMessageOut,WidgetConfigOut
from app.services.ai.rag import answer_question, classify_lead_response
from user_agents import parse as parse_ua
router = APIRouter(prefix="/widget", tags=["Widget"])


def _get_client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def _parse_device_info(request: Request) -> dict:
    ua_string = request.headers.get("user-agent", "")
    ua = parse_ua(ua_string)

    if ua.is_mobile:
        device_type = "mobile"
    elif ua.is_tablet:
        device_type = "tablet"
    elif ua.is_pc:
        device_type = "desktop"
    else:
        device_type = "unknown"

    return {
        "device_type": device_type,
        "browser": f"{ua.browser.family} {ua.browser.version_string}".strip(),
        "os": f"{ua.os.family} {ua.os.version_string}".strip(),
    }


@router.post("/message")
async def sent_widget_message(payload: WidgetMessageIn, request: Request, db: DbSession):
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
        device_info = _parse_device_info(request)
        conversation = Conversation(
            site_id=site.id,
            session_id=payload.session_id,
            visitor_id=payload.visitor_id,
            first_page_url=payload.first_page_url or payload.current_page_url,
            current_page_url=payload.current_page_url,
            referrer=payload.referrer,
            utm=payload.utm or {},
            gclid=payload.gclid,
            yclid=payload.yclid,
            metrika_client_id=payload.metrika_client_id,
            device_type=device_info["device_type"],
            browser=device_info["browser"],
            os=device_info["os"],
            ip_address=_get_client_ip(request),
        )
        db.add(conversation)
    else:
        conversation.current_page_url = payload.current_page_url

    await db.commit()
    await db.refresh(conversation)

    db.add(Message(conversation_id=conversation.id, role=MessageRole.user, content=payload.message))
    await db.commit()

    conversation.messages_since_last_offer += 1

    rag_result = await answer_question(
        db,
        site.id,
        payload.message,
        message_count=conversation.messages_since_last_offer,
    )

    clean_answer = rag_result["answer"].replace("\x00", "")

    if rag_result.get("ask_lead"):
        conversation.messages_since_last_offer = 0

    if rag_result.get("sources"):
        conversation.detected_interest = {"last_topic": rag_result["sources"][0]}

    await db.commit()

    db.add(
        Message(
            conversation_id=conversation.id,
            role=MessageRole.assistant,
            content=clean_answer,
            sources=rag_result["sources"],
        )
    )
    await db.commit()

    return {
        "conversation_id": conversation.id,
        "answer": clean_answer,
        "sources": rag_result["sources"],
        "ask_lead": rag_result.get("ask_lead", False)
    }


@router.post("/lead")
async def submit_lead(payload: LeadIn, db: DbSession):
    """Сохраняет заявку, связывая Клиента, Диалог и Лид."""
    
    clean_phone = "".join(filter(str.isdigit, payload.phone))
    if clean_phone.startswith('8') and len(clean_phone) == 11:
        clean_phone = '7' + clean_phone[1:]
    if len(clean_phone) == 10 and clean_phone.startswith('9'):
        clean_phone = '7' + clean_phone

    if len(clean_phone) != 11 or not clean_phone.startswith('7'):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Некорректный номер телефона")

    clean_phone = '+' + clean_phone

    result_client = await db.execute(
        select(Client).where(Client.site_id == payload.site_id, Client.phone == clean_phone)
    )
    client = result_client.scalar_one_or_none()

    if not client:
        client = Client(site_id=payload.site_id, phone=clean_phone, name=payload.name)
        db.add(client)
        await db.flush() 
    else:
        if not client.name or client.name != payload.name:
            client.name = payload.name

    result_conv = await db.execute(
        select(Conversation).where(
            Conversation.site_id == payload.site_id,
            Conversation.session_id == payload.session_id
        )
    )
    conversation = result_conv.scalar_one_or_none()
    
    if not conversation:
        conversation = Conversation(
            site_id=payload.site_id, 
            session_id=payload.session_id, 
            visitor_id="unknown"
        )
        db.add(conversation)
        await db.flush()

    conversation.client_id = client.id
    
    last_user_msg_result = await db.execute(
        select(Message.content)
        .where(Message.conversation_id == conversation.id, Message.role == MessageRole.user)
        .order_by(Message.created_at.desc())
        .limit(1)
    )
    last_msg_content = last_user_msg_result.scalar_one_or_none()
    
    lead = Lead(
        site_id=payload.site_id,
        conversation_id=conversation.id,
        client_id=client.id,
        name=payload.name,
        phone=clean_phone,
        interest={"last_question": last_msg_content or "Общий запрос"}, # Сохраняем реальный текст
        consent_text_version="v1.0"
    )
    
    db.add(lead)
    await db.commit()
    
    return {"status": "ok"}


@router.post("/classify-lead-response")
async def classify_lead(payload: dict, db: DbSession):
    """Определяет тип сообщения в процессе сбора лида."""
    message = payload.get("message", "")
    category = await classify_lead_response(message)
    return {"category": category}


@router.get("/config", response_model=WidgetConfigOut)
async def get_widget_config(site_id: uuid.UUID, db: DbSession):
    site = await db.get(Site, site_id)
    if site is None or not site.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Сайт не найден или отключён")

    return WidgetConfigOut(
        site_id=site.id,
        bot_name=site.widget_bot_name,
        welcome_message=site.widget_welcome_message,
        primary_color=site.widget_primary_color,
        logo_url=site.widget_logo_url,
    )