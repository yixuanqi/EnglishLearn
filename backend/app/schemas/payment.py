"""Payment schemas following api_spec.yaml."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema
from app.schemas.user import SubscriptionPlan


class BillingPeriod(str, Enum):
    """Billing period types."""

    MONTHLY = "monthly"
    ANNUAL = "annual"


class SubscriptionStatus(str, Enum):
    """Subscription status types."""

    ACTIVE = "active"
    PENDING = "pending"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    NONE = "none"


class SubscriptionPlanDetail(BaseSchema):
    """Subscription plan details."""

    id: SubscriptionPlan = Field(..., description="Plan ID")
    name: str = Field(..., description="Plan name")
    description: str = Field(..., description="Plan description")
    price: float = Field(..., description="Price amount")
    currency: str = Field(default="USD", description="Currency")
    billing_period: BillingPeriod = Field(..., description="Billing period")
    features: list[str] = Field(default_factory=list, description="Plan features")


class PlanListResponse(BaseModel):
    """Plan list response."""

    plans: list[SubscriptionPlanDetail] = Field(..., description="Available plans")


class CreateSubscriptionRequest(BaseModel):
    """Create subscription request."""

    plan_id: SubscriptionPlan = Field(..., description="Plan ID")
    payment_method_id: str = Field(..., description="Payment method ID")


class SubscriptionResponse(BaseSchema):
    """Subscription response."""

    subscription_id: str = Field(..., description="Subscription ID")
    status: str = Field(..., description="Subscription status")
    client_secret: Optional[str] = Field(
        None,
        description="Client secret for 3D Secure",
    )


class SubscriptionStatusResponse(BaseSchema):
    """Subscription status response."""

    plan: SubscriptionPlan = Field(..., description="Current plan")
    status: SubscriptionStatus = Field(..., description="Subscription status")
    current_period_start: Optional[datetime] = Field(
        None,
        description="Period start date",
    )
    current_period_end: Optional[datetime] = Field(
        None,
        description="Period end date",
    )
    cancel_at_period_end: bool = Field(
        default=False,
        description="Cancel at period end",
    )


class VerifyReceiptRequest(BaseModel):
    """Verify receipt request."""

    platform: str = Field(..., description="Platform (ios or android)")
    receipt_data: str = Field(..., description="Receipt data")


class VerifyReceiptResponse(BaseModel):
    """Verify receipt response."""

    success: bool = Field(..., description="Verification success")
    message: str = Field(..., description="Response message")
    subscription_status: Optional[str] = Field(
        None,
        description="Subscription status",
    )
    plan_type: Optional[str] = Field(None, description="Plan type")
    expires_date: Optional[datetime] = Field(None, description="Expiry date")


class SubscriptionPlanResponse(BaseSchema):
    """Subscription plan response."""

    id: str = Field(..., description="Plan ID")
    name: str = Field(..., description="Plan name")
    description: str = Field(..., description="Plan description")
    monthly_price: float = Field(..., description="Monthly price")
    annual_price: float = Field(..., description="Annual price")
    features: list[str] = Field(default_factory=list, description="Plan features")
    is_popular: bool = Field(default=False, description="Is popular plan")
