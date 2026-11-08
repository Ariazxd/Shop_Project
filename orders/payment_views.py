from django.conf import settings
from django.db import transaction
from rest_framework import permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from . import zarinpal
from .models import Order, Payment


class PayOrderView(APIView):
    """POST /api/orders/<id>/pay/ -> returns the Zarinpal URL the user must open."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        if order.status != Order.Status.PENDING:
            return Response(
                {"detail": f"Order is already {order.status}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        amount_rial = order.total_price * 10  # prices are stored in Toman
        try:
            authority, payment_url = zarinpal.request_payment(
                amount_rial=amount_rial,
                description=f"Order #{order.pk}",
                callback_url=settings.ZARINPAL_CALLBACK_URL,
            )
        except zarinpal.ZarinpalError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        Payment.objects.create(order=order, authority=authority, amount=amount_rial)
        return Response({"authority": authority, "payment_url": payment_url})


class VerifyPaymentView(APIView):
    """
    Zarinpal redirects the browser here: /api/payments/verify/?Authority=...&Status=OK|NOK
    No token is sent by the browser redirect, so this endpoint is public; it is safe
    because it only trusts the result that Zarinpal's verify API returns.
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        authority = request.query_params.get("Authority", "")
        callback_status = request.query_params.get("Status", "")

        payment = get_object_or_404(
            Payment.objects.select_related("order"), authority=authority
        )
        order = payment.order

        if payment.status == Payment.Status.PAID:
            return Response({"detail": "Payment already verified.", "order_id": order.pk,
                             "ref_id": payment.ref_id})

        if callback_status != "OK":
            self._fail(payment)
            return Response(
                {"detail": "Payment was cancelled or failed.", "order_id": order.pk},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            ref_id = zarinpal.verify_payment(payment.amount, authority)
        except zarinpal.ZarinpalError as exc:
            self._fail(payment)
            return Response(
                {"detail": str(exc), "order_id": order.pk},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            payment.status = Payment.Status.PAID
            payment.ref_id = ref_id
            payment.save(update_fields=["status", "ref_id", "updated_at"])
            order.status = Order.Status.PAID
            order.save(update_fields=["status", "updated_at"])

        return Response(
            {"detail": "Payment successful.", "order_id": order.pk, "ref_id": ref_id}
        )

    @staticmethod
    def _fail(payment):
        """Mark the payment and its order as failed."""
        with transaction.atomic():
            payment.status = Payment.Status.FAILED
            payment.save(update_fields=["status", "updated_at"])
            order = payment.order
            order.status = Order.Status.FAILED
            order.save(update_fields=["status", "updated_at"])
