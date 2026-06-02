from sqlalchemy import Column, Date, DateTime, Index, Integer, Numeric, String, UniqueConstraint, func
from app.database import Base


class PowerPrice(Base):
    __tablename__ = "power_prices"

    id = Column(Integer, primary_key=True, index=True)
    trade_date = Column(Date, nullable=False)
    country = Column(String(10), nullable=False)
    power_price_eur_mwh = Column(Numeric(12, 4), nullable=False)
    source = Column(String(100), nullable=False)
    loaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("trade_date", "country", name="uq_power_prices_trade_date_country"),
        Index("ix_power_prices_country_trade_date", "country", "trade_date"),
    )
