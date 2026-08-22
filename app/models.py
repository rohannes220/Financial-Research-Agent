from datetime import date
from sqlalchemy import String,Text,Integer,Date,Float,ForeignKey,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from pgvector.sqlalchemy import Vector
from app.db import Base
from app.config import settings

class Company(Base):
    __tablename__="companies"
    id:Mapped[int]=mapped_column(primary_key=True)
    ticker:Mapped[str]=mapped_column(String(16),unique=True,index=True)
    cik:Mapped[str]=mapped_column(String(16),unique=True)
    name:Mapped[str]=mapped_column(String(255),default="")

class Filing(Base):
    __tablename__="filings"
    id:Mapped[int]=mapped_column(primary_key=True)
    company_id:Mapped[int]=mapped_column(ForeignKey("companies.id"),index=True)
    accession:Mapped[str]=mapped_column(String(32),unique=True)
    form:Mapped[str]=mapped_column(String(16))
    filed_at:Mapped[date]=mapped_column(Date)
    source_url:Mapped[str]=mapped_column(Text)

class FilingChunk(Base):
    __tablename__="filing_chunks"
    id:Mapped[int]=mapped_column(primary_key=True)
    filing_id:Mapped[int]=mapped_column(ForeignKey("filings.id"),index=True)
    chunk_index:Mapped[int]=mapped_column(Integer)
    text:Mapped[str]=mapped_column(Text)
    section:Mapped[str]=mapped_column(String(64),default="other",index=True)
    embedding:Mapped[list]=mapped_column(Vector(settings.embedding_dim))
    __table_args__=(UniqueConstraint("filing_id","chunk_index"),)

class FinancialFact(Base):
    __tablename__="financial_facts"
    id:Mapped[int]=mapped_column(primary_key=True)
    company_id:Mapped[int]=mapped_column(ForeignKey("companies.id"),index=True)
    taxonomy:Mapped[str]=mapped_column(String(32))
    concept:Mapped[str]=mapped_column(String(255),index=True)
    label:Mapped[str]=mapped_column(String(255),default="")
    unit:Mapped[str]=mapped_column(String(32))
    value:Mapped[float]=mapped_column(Float)
    start:Mapped[date|None]=mapped_column(Date,nullable=True)
    end:Mapped[date]=mapped_column(Date)
    fy:Mapped[int|None]=mapped_column(Integer,nullable=True)
    fp:Mapped[str|None]=mapped_column(String(16),nullable=True)
    form:Mapped[str|None]=mapped_column(String(16),nullable=True)
    accession:Mapped[str|None]=mapped_column(String(32),nullable=True)
