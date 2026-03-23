"""Payment and subscription API endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.payment import Payment, SubscriptionPlan
from app.schemas.payment import (
    VerifyReceiptRequest,
    VerifyReceiptResponse,
    SubscriptionStatusResponse,
    SubscriptionPlanResponse,
    PlanListResponse,
)
from app.services.payment_verification import PaymentVerificationService, PaymentVerificationError

router = APIRouter(prefix="/payments", tags=["Payments"])

verification_service = PaymentVerificationService()


@router.post("/verify", response_model=VerifyReceiptResponse)
async def verify_receipt(
    request: VerifyReceiptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify in-app purchase receipt.
    
    This endpoint verifies purchase receipts from iOS (App Store) or Android (Google Play).
    After successful verification, the user's subscription is activated.
    """
    try:
        receipt_data = await verification_service.verify_receipt(
            platform=request.platform,
            receipt_data=request.receipt_data,
        )
    except PaymentVerificationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    product_id = receipt_data["product_id"]
    plan_type = verification_service.get_plan_from_product_id(product_id)
    
    existing_payment = await db.execute(
        select(Payment).where(
            Payment.transaction_id == receipt_data["transaction_id"]
        )
    )
    existing_payment = existing_payment.scalar_one_or_none()
    
    if existing_payment:
        if existing_payment.status == "completed":
            return VerifyReceiptResponse(
                success=True,
                message="Receipt already verified",
                subscription_status=existing_payment.status,
            )
        else:
            await db.delete(existing_payment)
    
    payment = Payment(
        user_id=current_user.id,
        plan_type=plan_type,
        platform=receipt_data["platform"],
        amount=_get_plan_price(plan_type),
        currency="USD",
        status="completed",
        transaction_id=receipt_data["transaction_id"],
        stripe_payment_intent_id=receipt_data["transaction_id"],
        purchase_date=receipt_data["purchase_date"],
        next_billing_date=receipt_data.get("expires_date"),
    )
    
    db.add(payment)
    
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(
            subscription_plan=plan_type,
            is_premium=True,
        )
    )
    
    await db.commit()
    
    return VerifyReceiptResponse(
        success=True,
        message="Receipt verified successfully",
        subscription_status="active",
        plan_type=plan_type,
        expires_date=receipt_data.get("expires_date"),
    )


@router.get("/subscription", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's subscription status.
    
    Returns details about the user's active subscription, including plan type,
    expiry date, and available features.
    """
    latest_payment = await db.execute(
        select(Payment)
        .where(Payment.user_id == current_user.id)
        .where(Payment.status == "completed")
        .order_by(Payment.created_at.desc())
        .limit(1)
    )
    latest_payment = latest_payment.scalar_one_or_none()
    
    is_active = False
    expires_date = None
    
    if latest_payment:
        if latest_payment.next_billing_date:
            is_active = latest_payment.next_billing_date > datetime.utcnow()
            expires_date = latest_payment.next_billing_date
        else:
            is_active = True
    
    if not is_active:
        await db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(
                subscription_plan="free",
                is_premium=False,
            )
        )
        await db.commit()
    
    return SubscriptionStatusResponse(
        plan=current_user.subscription_plan,
        is_active=is_active,
        is_premium=current_user.is_premium,
        expires_date=expires_date,
        features=_get_plan_features(current_user.subscription_plan),
    )


@router.get("/plans", response_model=PlanListResponse)
async def get_subscription_plans():
    """
    Get available subscription plans.
    
    Returns a list of all available subscription plans with their pricing and features.
    """
    plans = [
        SubscriptionPlanResponse(
            id="free",
            name="Free",
            description="Basic features for casual learners",
            monthly_price=0.0,
            annual_price=0.0,
            features=[
                "5 scenarios per category",
                "Basic pronunciation evaluation",
                "10 practice sessions per week",
                "Practice history (7 days)",
            ],
            is_popular=False,
        ),
        SubscriptionPlanResponse(
            id="premium_monthly",
            name="Premium Monthly",
            description="Full access for serious learners",
            monthly_price=9.99,
            annual_price=0.0,
            features=[
                "Unlimited scenarios",
                "Advanced evaluation (word/phoneme level)",
                "Unlimited practice sessions",
                "Custom scenario generation (3/month)",
                "Full practice history",
                "Learning reports",
                "Priority support",
            ],
            is_popular=True,
        ),
        SubscriptionPlanResponse(
            id="premium_annual",
            name="Premium Annual",
            description="Best value - Save 33%",
            monthly_price=0.0,
            annual_price=79.99,
            features=[
                "All Premium features",
                "Custom scenario generation (10/month)",
                "Early access to new features",
                "Priority support",
            ],
            is_popular=False,
        ),
    ]
    
    return PlanListResponse(plans=plans)


@router.post("/subscription/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel current subscription.
    
    Cancels the user's active subscription. Access continues until the end of the billing period.
    """
    if current_user.subscription_plan == "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription to cancel",
        )
    
    latest_payment = await db.execute(
        select(Payment)
        .where(Payment.user_id == current_user.id)
        .where(Payment.status == "completed")
        .order_by(Payment.created_at.desc())
        .limit(1)
    )
    latest_payment = latest_payment.scalar_one_or_none()
    
    if latest_payment:
        latest_payment.status = "cancelled"
        await db.commit()
    
    return {
        "message": "Subscription cancelled successfully",
        "expires_date": latest_payment.next_billing_date if latest_payment else None,
    }


def _get_plan_price(plan_type: str) -> float:
    """Get price for a plan type."""
    prices = {
        "premium_monthly": 9.99,
        "premium_annual": 79.99,
    }
    return prices.get(plan_type, 0.0)


def _get_plan_features(plan_type: str) -> list:
    """Get features for a plan type."""
    features = {
        "free": [
            "5 scenarios per category",
            "Basic pronunciation evaluation",
            "10 practice sessions per week",
            "Practice history (7 days)",
        ],
        "premium_monthly": [
            "Unlimited scenarios",
            "Advanced evaluation (word/phoneme level)",
            "Unlimited practice sessions",
            "Custom scenario generation (3/month)",
            "Full practice history",
            "Learning reports",
            "Priority support",
        ],
        "premium_annual": [
            "All Premium features",
            "Custom scenario generation (10/month)",
            "Early access to new features",
            "Priority support",
        ],
    }
    return features.get(plan_type, [])
