from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, hash_password
from app.models.conversation import Conversation
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.schemas.admin import AdminAgentOut, AdminConversationOut, AssignAgentRequest, CreateAgentRequest, SettingsOut, SettingsUpdate
from app.services.audit_service import record_activity

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_superuser and user.role not in {UserRole.ADMIN, UserRole.OWNER}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return user


@router.get("/conversations", response_model=list[AdminConversationOut])
async def list_admin_conversations(
    status_filter: str | None = Query(None, alias="status"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(Conversation).where(Conversation.organization_id == current_user.organization_id)
    if status_filter:
        query = query.where(Conversation.status == status_filter)
    result = await db.execute(query.order_by(Conversation.updated_at.desc()))
    return result.scalars().all()


@router.post("/conversations/{id}/assign", response_model=AdminConversationOut)
async def admin_assign_conversation(
    id: int,
    data: AssignAgentRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    conversation = (await db.execute(select(Conversation).where(
        Conversation.id == id, Conversation.organization_id == current_user.organization_id,
    ))).scalar_one_or_none()
    agent = (await db.execute(select(User).where(
        User.id == data.agent_id, User.organization_id == current_user.organization_id,
        User.role.in_([UserRole.AGENT, UserRole.ADMIN, UserRole.OWNER]),
    ))).scalar_one_or_none()
    if not conversation or not agent:
        raise HTTPException(status_code=404, detail="Conversation or agent not found")
    previous = conversation.assigned_to
    conversation.assigned_to = agent.id
    await record_activity(db, organization_id=current_user.organization_id, user_id=current_user.id,
                          conversation_id=id, actor="admin", action_type="assign",
                          description="Conversation assigned", details={"previous": previous, "agent_id": agent.id})
    await db.commit()
    await db.refresh(conversation)
    return conversation


@router.get("/agents", response_model=list[AdminAgentOut])
async def list_agents(current_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.organization_id == current_user.organization_id))
    return result.scalars().all()


@router.post("/agents", response_model=AdminAgentOut, status_code=201)
async def create_agent(data: CreateAgentRequest, current_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    if data.role not in {role.value for role in UserRole}:
        raise HTTPException(status_code=400, detail="Invalid role")
    existing = (await db.execute(select(User).where(User.email == data.email))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    agent = User(email=data.email, full_name=data.full_name, hashed_password=hash_password(data.password),
                 organization_id=current_user.organization_id, role=UserRole(data.role))
    db.add(agent)
    await record_activity(db, organization_id=current_user.organization_id, user_id=current_user.id,
                          actor="admin", action_type="agent_create", description="Agent created",
                          details={"email": data.email, "role": data.role})
    await db.commit()
    await db.refresh(agent)
    return agent


async def _settings(kind: str, current_user: User, db: AsyncSession) -> SettingsOut:
    organization = await db.get(Organization, current_user.organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return SettingsOut(organization_id=organization.id, values=getattr(organization, kind) or {})


async def _update_settings(kind: str, data: SettingsUpdate, current_user: User, db: AsyncSession) -> SettingsOut:
    organization = await db.get(Organization, current_user.organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    previous = getattr(organization, kind) or {}
    setattr(organization, kind, data.values)
    await record_activity(db, organization_id=current_user.organization_id, user_id=current_user.id,
                          actor="admin", action_type=f"{kind}_update", description="Settings updated",
                          details={"previous": previous, "values": data.values})
    await db.commit()
    return SettingsOut(organization_id=organization.id, values=data.values)


@router.get("/organization/settings", response_model=SettingsOut)
async def get_organization_settings(current_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    return await _settings("settings", current_user, db)


@router.patch("/organization/settings", response_model=SettingsOut)
async def update_organization_settings(data: SettingsUpdate, current_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    return await _update_settings("settings", data, current_user, db)


@router.get("/ai/settings", response_model=SettingsOut)
async def get_ai_settings(current_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    return await _settings("ai_settings", current_user, db)


@router.patch("/ai/settings", response_model=SettingsOut)
async def update_ai_settings(data: SettingsUpdate, current_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    return await _update_settings("ai_settings", data, current_user, db)
