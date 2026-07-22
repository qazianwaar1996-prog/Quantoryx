# backend/models/models.py
"""
Quantoryx — Relational Database Models.

This module maps out all database schema tables utilizing the SQLAlchemy ORM.
It defines relationships, strict constraint indexes, JSON data column mappings,
and operational audit logging structures portable across SQLite and PostgreSQL.
"""

from datetime import datetime
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.database.connection import Base


# =====================================================================
# USER IDENTITY & METADATA SCHEMAS
# =====================================================================

class User(Base):
    """Stores credentials, security role contexts, and profile states."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), nullable=False, default="user")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relational bindings
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    strategies = relationship("SavedStrategy", back_populates="user", cascade="all, delete-orphan")
    backtests = relationship("SavedBacktest", back_populates="user", cascade="all, delete-orphan")
    optimizations = relationship("SavedOptimization", back_populates="user", cascade="all, delete-orphan")
    ai_analyses = relationship("SavedAIAnalysis", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("SavedReport", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


class UserSettings(Base):
    """Stores customized default operational configurations per user profile."""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    default_symbol = Column(String(20), nullable=False, default="EURUSD")
    default_timeframe = Column(String(10), nullable=False, default="1H")
    risk_per_trade_pct = Column(Float, nullable=False, default=1.0)
    leverage = Column(Float, nullable=False, default=30.0)
    spread = Column(Float, nullable=False, default=0.0002)
    confidence_threshold = Column(Float, nullable=False, default=65.0)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relational bindings
    user = relationship("User", back_populates="settings")


# =====================================================================
# SAVED QUANTITATIVE ARTIFACT SCHEMAS
# =====================================================================

class SavedStrategy(Base):
    """Stores saved strategy parameter configurations."""
    __tablename__ = "saved_strategies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False)
    config_key = Column(String(50), nullable=False)
    parameters = Column(JSON, nullable=False)
    is_favorite = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relational bindings
    user = relationship("User", back_populates="strategies")


class SavedBacktest(Base):
    """Stores completed backtest simulation metrics and parameters."""
    __tablename__ = "saved_backtests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    strategy_name = Column(String(50), nullable=False)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    parameters = Column(JSON, nullable=False)
    net_profit = Column(Float, nullable=False)
    profit_factor = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    win_rate = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=False)
    trade_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relational bindings
    user = relationship("User", back_populates="backtests")


class SavedOptimization(Base):
    """Stores parameter sweeps, combinations tested, and ranking metadata."""
    __tablename__ = "saved_optimizations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    strategy_name = Column(String(50), nullable=False)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    ranking_metric = Column(String(50), nullable=False)
    best_parameters = Column(JSON, nullable=False)
    total_combinations_tested = Column(Integer, nullable=False)
    top_results = Column(JSON, nullable=False)  # Stores top 10 ranked runs summary JSON
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relational bindings
    user = relationship("User", back_populates="optimizations")


class SavedAIAnalysis(Base):
    """Stores cognitive AI strategy selection trace history parameters."""
    __tablename__ = "saved_ai_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    market_regime = Column(String(50), nullable=False)
    selected_strategy = Column(String(50), nullable=False)
    confidence_score = Column(Float, nullable=False)
    decision_action = Column(String(20), nullable=False)
    explanation = Column(Text, nullable=False)
    parameters = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relational bindings
    user = relationship("User", back_populates="ai_analyses")


class SavedReport(BaseModel):
    """Stores metadata of CSV outputs and ledger files compiled on disk."""
    __tablename__ = "saved_reports"

    # We map this class using Base to keep base definitions correct
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    size_kb = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relational bindings
    user = relationship("User", back_populates="reports")


# Inject Base metadata explicitly to allow SavedReport Base binding correctly
# SQLAlchemy requires manual Base re-association if name classes are modified
SavedReport = type('SavedReport', (Base,), dict(SavedReport.__dict__))


# =====================================================================
# SYSTEM AUDIT LOGGING SCHEMA
# =====================================================================

class AuditLog(Base):
    """Tracks critical system events, access controls, and operational tracing."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)  # e.g., "USER_LOGIN", "BACKTEST_RUN"
    entity_type = Column(String(50), nullable=True)  # e.g., "backtest", "strategy"
    entity_id = Column(String(50), nullable=True)
    ip_address = Column(String(45), nullable=True)
    details = Column(Text, nullable=True)  # Store serialized event parameters
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relational bindings
    user = relationship("User", back_populates="audit_logs")
