import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from products.models import Category, Product

CATALOG = {
    "Electronics": [
        ("Wireless Headphones", 1_850_000),
        ("Bluetooth Speaker", 1_200_000),
        ("Smart Watch", 3_400_000),
        ("Power Bank 20000mAh", 890_000),
        ("USB-C Charger 65W", 650_000),
    ],
    "Books": [
        ("Learning Python", 520_000),
        ("Django for Beginners", 430_000),
        ("Clean Code", 480_000),
        ("The Pragmatic Programmer", 510_000),
    ],
    "Clothing": [
        ("Cotton T-Shirt", 350_000),
        ("Denim Jacket", 1_900_000),
        ("Running Shoes", 2_700_000),
        ("Wool Scarf", 420_000),
    ],
    "Home": [
        ("Ceramic Mug", 120_000),
        ("Desk Lamp", 760_000),
        ("Coffee Maker", 2_300_000),
        ("Throw Pillow", 280_000),
    ],
}


class Command(BaseCommand):
    help = "Seed the database with demo categories, products and an admin user."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing products and categories before seeding.",
        )
        parser.add_argument("--admin-username", default="admin")
        parser.add_argument("--admin-password", default="admin12345")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing catalog deleted."))

        rng = random.Random(42)  # deterministic demo data
        created_products = 0

        for category_name, items in CATALOG.items():
            category, _ = Category.objects.get_or_create(
                name=category_name, defaults={"slug": slugify(category_name)}
            )
            for name, price in items:
                _, created = Product.objects.get_or_create(
                    name=name,
                    category=category,
                    defaults={
                        "description": f"{name} - demo product in {category_name}.",
                        "price": price,
                        "stock": rng.choice([0, 3, 10, 25, 50]),
                    },
                )
                created_products += int(created)

        User = get_user_model()
        username = options["admin_username"]
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=f"{username}@example.com",
                password=options["admin_password"],
            )
            self.stdout.write(f"Created admin user '{username}'.")

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {Category.objects.count()} categories, "
                f"{Product.objects.count()} products ({created_products} new)."
            )
        )
