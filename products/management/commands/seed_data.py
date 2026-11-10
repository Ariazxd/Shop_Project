import random
from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from accounts.models import Profile
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

# Development-only accounts with a fixed password (see --user-password).
TEST_USERS = [
    {
        "username": "user1",
        "email": "user1@example.com",
        "phone": "09120000001",
        "address": "Tehran, Valiasr St., No. 12",
        "birth_date": date(1995, 4, 12),
    },
    {
        "username": "user2",
        "email": "user2@example.com",
        "phone": "09120000002",
        "address": "Isfahan, Chahar Bagh St., No. 7",
        "birth_date": date(1990, 9, 23),
    },
]


class Command(BaseCommand):
    help = (
        "Seed the database with demo categories, products, an admin user and "
        "test users with filled profiles. Development only."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing products, categories and the seeded test users first.",
        )
        parser.add_argument(
            "--minimal",
            action="store_true",
            help="Seed only the catalog and the admin user (no test users).",
        )
        parser.add_argument(
            "--force-test-data",
            action="store_true",
            help="Create test users even when DJANGO_DEBUG is off.",
        )
        parser.add_argument("--admin-username", default="admin")
        parser.add_argument("--admin-password", default="admin12345")
        parser.add_argument("--user-password", default="user12345")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            self._clear()

        created_products = self._seed_catalog()
        self._seed_admin(options["admin_username"], options["admin_password"])

        seeded_users = 0
        if options["minimal"]:
            pass
        elif not settings.DEBUG and not options["force_test_data"]:
            self.stdout.write(
                self.style.WARNING(
                    "DEBUG is off: test users were NOT created "
                    "(use --force-test-data to override)."
                )
            )
        else:
            seeded_users = len(self._seed_test_users(options["user_password"]))

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {Category.objects.count()} categories, "
                f"{Product.objects.count()} products ({created_products} new), "
                f"{seeded_users} test users."
            )
        )

    def _clear(self):
        User = get_user_model()
        test_usernames = [u["username"] for u in TEST_USERS]
        User.objects.filter(username__in=test_usernames).delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write(self.style.WARNING("Existing catalog and test users deleted."))

    def _seed_catalog(self):
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
        return created_products

    def _seed_admin(self, username, password):
        User = get_user_model()
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username, email=f"{username}@example.com", password=password
            )
            self.stdout.write(f"Created admin user '{username}'.")

    def _seed_test_users(self, password):
        """Create the test users and fill the (signal-created) empty profiles."""
        User = get_user_model()
        users = {}
        for data in TEST_USERS:
            user = User.objects.filter(username=data["username"]).first()
            if user is None:
                user = User.objects.create_user(
                    username=data["username"], email=data["email"], password=password
                )
                self.stdout.write(f"Created test user '{user.username}'.")
            profile, _ = Profile.objects.get_or_create(user=user)
            # Only fill what is still empty, so edits made through the API survive.
            if not profile.phone:
                profile.phone = data["phone"]
            if not profile.address:
                profile.address = data["address"]
            if profile.birth_date is None:
                profile.birth_date = data["birth_date"]
            profile.save()
            users[user.username] = user
        return users
