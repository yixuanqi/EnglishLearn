"""Dialogue model matching database_schema.md."""

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.scenario import Scenario


class Dialogue(Base):
    """Dialogue model for generated conversations."""

    __tablename__ = "dialogues"

    scenario_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("scenarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    variation: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    content: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )
    generated_by: Mapped[str] = mapped_column(
        String(50),
        default="openai",
        nullable=False,
    )
    generation_params: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("scenario_id", "variation", name="uq_dialogues_scenario_variation"),
        CheckConstraint(
            "variation >= 1 AND variation <= 10",
            name="chk_variation",
        ),
    )

    scenario: Mapped["Scenario"] = relationship(
        "Scenario",
        back_populates="dialogues",
    )
