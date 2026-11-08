"""Minimal Zarinpal v4 client (sandbox or production, see settings.ZARINPAL_SANDBOX)."""
import requests
from django.conf import settings

TIMEOUT = 15


class ZarinpalError(Exception):
    pass


def _base_url():
    if settings.ZARINPAL_SANDBOX:
        return "https://sandbox.zarinpal.com"
    return "https://payment.zarinpal.com"


def _post(path, payload):
    try:
        resp = requests.post(
            f"{_base_url()}{path}",
            json=payload,
            headers={"Accept": "application/json"},
            timeout=TIMEOUT,
        )
        body = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise ZarinpalError(f"Could not reach Zarinpal: {exc}") from exc

    data = body.get("data") or {}
    if not isinstance(data, dict):  # Zarinpal returns [] when there is an error
        data = {}
    errors = body.get("errors")
    return data, errors


def request_payment(amount_rial, description, callback_url):
    """Create a payment session. Returns (authority, start_pay_url)."""
    data, errors = _post(
        "/pg/v4/payment/request.json",
        {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": amount_rial,
            "callback_url": callback_url,
            "description": description,
        },
    )
    if data.get("code") != 100 or not data.get("authority"):
        raise ZarinpalError(f"Payment request rejected: {errors or data}")
    authority = data["authority"]
    return authority, f"{_base_url()}/pg/StartPay/{authority}"


def verify_payment(amount_rial, authority):
    """Verify a payment. Returns ref_id on success, raises ZarinpalError otherwise."""
    data, errors = _post(
        "/pg/v4/payment/verify.json",
        {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": amount_rial,
            "authority": authority,
        },
    )
    # 100 = verified now, 101 = was already verified before
    if data.get("code") not in (100, 101):
        raise ZarinpalError(f"Payment verification failed: {errors or data}")
    return str(data.get("ref_id", ""))
