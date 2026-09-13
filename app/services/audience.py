from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.services.broadcast import AudienceResolver, CustomerRecord

logger = logging.getLogger(__name__)

MAX_AUDIENCE_SIZE = 5000


class DefaultAudienceResolver(AudienceResolver):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def resolve(self, organization_id: int, audience_filter: dict) -> list[CustomerRecord]:
        query = select(Customer).where(Customer.organization_id == organization_id)

        customer_ids = audience_filter.get("customer_ids")
        saved_query_id = audience_filter.get("saved_query_id")
        tags = audience_filter.get("tags")
        segment_id = audience_filter.get("segment_id")

        if customer_ids:
            query = query.where(Customer.id.in_(customer_ids))

        elif saved_query_id:
            saved_query = await self._load_saved_query(organization_id, saved_query_id)
            if saved_query is None:
                logger.warning("Saved query %s not found for org %s", saved_query_id, organization_id)
                return []
            query = self._apply_saved_query(query, saved_query)

        elif tags:
            query = query.where(
                or_(*[Customer.tags.contains([tag]) for tag in tags])
            )

        elif segment_id:
            query = query.where(Customer.segment_id == segment_id)

        else:
            logger.warning("Empty audience_filter for org %s — resolving to zero recipients", organization_id)
            return []

        query = query.limit(MAX_AUDIENCE_SIZE)

        result = await self.db.execute(query)
        customers = result.scalars().all()

        return [self._to_record(c) for c in customers]

    def _to_record(self, customer: Customer) -> CustomerRecord:
        return CustomerRecord(
            id=customer.id,
            organization_id=customer.organization_id,
            whatsapp_opt_in=bool(getattr(customer, "whatsapp_opt_in", False)),
            sms_opt_in=bool(getattr(customer, "sms_opt_in", False)),
            email_opt_in=bool(getattr(customer, "email_opt_in", False)),
            has_open_whatsapp_session=self._has_open_session(customer),
            phone=getattr(customer, "phone", None),
            email=getattr(customer, "email", None),
        )

    def _has_open_session(self, customer: Customer) -> bool:
        last_inbound_at = getattr(customer, "last_whatsapp_inbound_at", None)
        if not last_inbound_at:
            return False
        return datetime.now(timezone.utc) - last_inbound_at < timedelta(hours=24)

    async def _load_saved_query(self, organization_id: int, saved_query_id: str):
        return None

    def _apply_saved_query(self, query, saved_query):
        return query