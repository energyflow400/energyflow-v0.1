from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.power_price import PowerPrice

router = APIRouter(prefix="/prices", tags=["prices"])


class PowerPriceResponse(BaseModel):
    trade_date: date
    country: str
    power_price_eur_mwh: Decimal
    source: str
    loaded_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=list[PowerPriceResponse])
def get_prices(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[PowerPrice]:
    query = select(PowerPrice).order_by(desc(PowerPrice.trade_date)).limit(limit)
    return list(db.scalars(query).all())


@router.get("/latest", response_model=list[PowerPriceResponse])
def get_latest_prices(db: Session = Depends(get_db)) -> list[PowerPrice]:
    latest_date = db.scalar(select(PowerPrice.trade_date).order_by(desc(PowerPrice.trade_date)).limit(1))
    if latest_date is None:
        return []
    query = select(PowerPrice).where(PowerPrice.trade_date == latest_date).order_by(PowerPrice.country)
    return list(db.scalars(query).all())


@router.get("/country/{country}", response_model=list[PowerPriceResponse])
def get_prices_by_country(
    country: str,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[PowerPrice]:
    query = (
        select(PowerPrice)
        .where(PowerPrice.country == country.upper())
        .order_by(desc(PowerPrice.trade_date))
        .limit(limit)
    )
    return list(db.scalars(query).all())
