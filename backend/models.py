from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


# =========================================================
# REVIEWS
# =========================================================

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    review_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )

    review_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    redacted_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    sentiment: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    positive_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    neutral_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    negative_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    evidence_links = relationship(
        "EvidenceLink",
        back_populates="review",
        cascade="all, delete-orphan",
    )


# =========================================================
# INSIGHTS
# =========================================================

class Insight(Base):
    __tablename__ = "insights"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    insight_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    evidence_links = relationship(
        "EvidenceLink",
        back_populates="insight",
        cascade="all, delete-orphan",
    )


# =========================================================
# EVIDENCE LINKS
# =========================================================

class EvidenceLink(Base):
    __tablename__ = "evidence_links"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    insight_id: Mapped[int] = mapped_column(
        ForeignKey("insights.id"),
        nullable=False,
    )

    review_id: Mapped[str] = mapped_column(
        ForeignKey("reviews.id"),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    search_score: Mapped[float] = mapped_column(
        Float,
        nullable=True,
    )

    insight = relationship(
        "Insight",
        back_populates="evidence_links",
    )

    review = relationship(
        "Review",
        back_populates="evidence_links",
    )


# =========================================================
# SENTIMENT VALIDATION RESULTS
# =========================================================

class ValidationResult(Base):
    __tablename__ = "validation_results"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    sample_size: Mapped[int] = mapped_column(
        nullable=False,
    )

    accuracy: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    precision: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    recall: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    f1_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
class DriftResult(Base):
    __tablename__ = "drift_results"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    current_period: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    baseline_period: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    baseline_negative_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    current_negative_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    negative_rate_change: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    drift_detected: Mapped[bool] = mapped_column(
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )