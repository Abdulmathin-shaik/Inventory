from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SKU(Base):
    __tablename__ = 'skus'
    id = Column(Integer, primary_key=True)
    sku_code = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    reorder_point = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)


def create_database(engine):
    Base.metadata.create_all(engine)
