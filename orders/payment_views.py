from django.conf import settings
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
