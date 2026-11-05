from django.conf import settings
from django.db import models

from products.models import Product


class Basket(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="basket"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Basket of {self.user.username}"

    @property
    def total_price(self):
        return sum(item.line_total for item in self.items.select_related("product"))

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["basket", "product"], name="unique_product_per_basket"
            )
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def line_total(self):
        return self.quantity * self.product.price
