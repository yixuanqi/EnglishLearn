"""Payment verification service for in-app purchases."""

import json
import httpx
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.exceptions import AppException


class PaymentVerificationError(AppException):
    """Payment verification failed."""
    pass


class ReceiptVerifier:
    """Base class for receipt verification."""
    
    async def verify(self, receipt_data: str) -> Dict[str, Any]:
        """Verify receipt and return parsed data."""
        raise NotImplementedError


class AppleReceiptVerifier(ReceiptVerifier):
    """Apple App Store receipt verifier."""
    
    def __init__(self):
        self.verify_url = (
            "https://buy.itunes.apple.com/verifyReceipt"
            if settings.ENVIRONMENT == "production"
            else "https://sandbox.itunes.apple.com/verifyReceipt"
        )
        self.password = settings.APPLE_SHARED_SECRET
    
    async def verify(self, receipt_data: str) -> Dict[str, Any]:
        """Verify Apple receipt."""
        payload = {
            "receipt-data": receipt_data,
            "password": self.password,
            "exclude-old-transactions": True,
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.verify_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            
            if response.status_code != 200:
                raise PaymentVerificationError(
                    "Failed to verify Apple receipt"
                )
            
            result = response.json()
            
            if result.get("status") != 0:
                status_code = result.get("status")
                error_messages = {
                    21000: "Invalid JSON",
                    21002: "Invalid receipt data",
                    21003: "Receipt not authenticated",
                    21004: "Invalid shared secret",
                    21005: "Receipt server unavailable",
                    21007: "Receipt is from test environment",
                    21008: "Invalid receipt (production)",
                    21009: "Internal data error",
                    21010: "Receipt not authorized",
                }
                message = error_messages.get(
                    status_code,
                    f"Receipt verification failed (code: {status_code})",
                )
                raise PaymentVerificationError(message)
            
            return self._parse_receipt(result)
    
    def _parse_receipt(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Apple receipt data."""
        receipt = result.get("receipt", {})
        latest_receipt_info = result.get("latest_receipt_info", [])
        
        if not latest_receipt_info:
            raise PaymentVerificationError("No transactions found")
        
        latest_transaction = latest_receipt_info[0]
        
        product_id = latest_transaction.get("product_id")
        transaction_id = latest_transaction.get("transaction_id")
        purchase_date = int(latest_transaction.get("purchase_date_ms", 0)) / 1000
        expires_date_ms = latest_transaction.get("expires_date_ms")
        
        expires_date = None
        if expires_date_ms:
            expires_date = datetime.fromtimestamp(int(expires_date_ms) / 1000)
        
        is_trial = latest_transaction.get("is_trial_period", "false") == "true"
        is_intro = latest_transaction.get("is_in_intro_offer_period", "false") == "true"
        
        return {
            "platform": "ios",
            "product_id": product_id,
            "transaction_id": transaction_id,
            "purchase_date": datetime.fromtimestamp(purchase_date),
            "expires_date": expires_date,
            "is_trial": is_trial,
            "is_intro": is_intro,
            "original_transaction_id": latest_transaction.get("original_transaction_id"),
        }


class GoogleReceiptVerifier(ReceiptVerifier):
    """Google Play receipt verifier."""
    
    def __init__(self):
        self.api_url = f"https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{settings.GOOGLE_PACKAGE_NAME}/purchases/subscriptions"
        self.service_account_json = settings.GOOGLE_SERVICE_ACCOUNT_JSON
    
    async def verify(self, purchase_token: str) -> Dict[str, Any]:
        """Verify Google Play subscription."""
        import google.oauth2.service_account as oauth2
        import googleapiclient.discovery as discovery
        
        try:
            credentials = oauth2.Credentials.from_service_account_info(
                json.loads(self.service_account_json),
                scopes=["https://www.googleapis.com/auth/androidpublisher"],
            )
            
            service = discovery.build(
                "androidpublisher",
                "v3",
                credentials=credentials,
            )
            
            product_id = self._extract_product_id(purchase_token)
            
            result = (
                service.purchases()
                .subscriptions()
                .get(
                    packageName=settings.GOOGLE_PACKAGE_NAME,
                    subscriptionId=product_id,
                    token=purchase_token,
                )
                .execute()
            )
            
            return self._parse_subscription(result, product_id)
            
        except Exception as e:
            raise PaymentVerificationError(
                f"Failed to verify Google receipt: {str(e)}"
            )
    
    def _extract_product_id(self, purchase_token: str) -> str:
        """Extract product ID from purchase token."""
        return purchase_token.split(":")[0] if ":" in purchase_token else "premium_monthly"
    
    def _parse_subscription(
        self,
        result: Dict[str, Any],
        product_id: str,
    ) -> Dict[str, Any]:
        """Parse Google subscription data."""
        start_time = result.get("startTimeMillis", 0)
        expiry_time = result.get("expiryTimeMillis", 0)
        
        payment_state = result.get("paymentState")
        is_active = payment_state == 1
        
        cancel_reason = result.get("cancelReason", 0)
        is_trial = cancel_reason == 1
        
        return {
            "platform": "android",
            "product_id": product_id,
            "transaction_id": result.get("orderId"),
            "purchase_date": datetime.fromtimestamp(int(start_time) / 1000),
            "expires_date": datetime.fromtimestamp(int(expiry_time) / 1000),
            "is_trial": is_trial,
            "is_intro": False,
            "is_active": is_active,
            "cancel_reason": cancel_reason,
        }


class PaymentVerificationService:
    """Service for verifying payments from multiple platforms."""
    
    def __init__(self):
        self.apple_verifier = AppleReceiptVerifier()
        self.google_verifier = GoogleReceiptVerifier()
    
    async def verify_receipt(
        self,
        platform: str,
        receipt_data: str,
    ) -> Dict[str, Any]:
        """Verify receipt from specified platform."""
        if platform == "ios":
            return await self.apple_verifier.verify(receipt_data)
        elif platform == "android":
            return await self.google_verifier.verify(receipt_data)
        else:
            raise PaymentVerificationError(
                f"Unsupported platform: {platform}"
            )
    
    def get_plan_from_product_id(self, product_id: str) -> str:
        """Map product ID to subscription plan."""
        plan_mapping = {
            "com.englishtrainer.premium.monthly": "premium_monthly",
            "com.englishtrainer.premium.annual": "premium_annual",
            "premium_monthly": "premium_monthly",
            "premium_annual": "premium_annual",
        }
        return plan_mapping.get(product_id, "premium_monthly")
