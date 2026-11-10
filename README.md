# Shop API

A Django REST Framework shop backend. API only, no templates / no frontend.

## Features

- Sign up / sign in / sign out (token authentication)
- Profile: detail, update, delete (no list endpoint)
- Products: list, detail, create, update, delete (write access: staff only)
- Search, filter and ordering on the product list
- Basket (add, change quantity, remove, clear)
- Purchase (basket -> order, stock is reserved)
- Payment through Zarinpal **sandbox**
- `seed_data` management command for demo data (catalog, test users, basket, orders)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations accounts products orders
python manage.py migrate
python manage.py seed_data         # demo data, see "Demo data" below
python manage.py runserver
```

Optional environment variables: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`,
`ZARINPAL_MERCHANT_ID`, `ZARINPAL_CALLBACK_URL`, `ZARINPAL_SANDBOX` (default `1`).

## Demo data

> **For development only.** The seeded accounts use well-known passwords. Never
> run this against a production database (the test users are skipped when
> `DJANGO_DEBUG=0` unless you pass `--force-test-data`).

```bash
python manage.py seed_data              # everything below
python manage.py seed_data --minimal    # catalog + admin only
python manage.py seed_data --no-orders  # + test users, but no basket/orders
python manage.py seed_data --clear      # delete orders, catalog and test users first
python manage.py seed_data --admin-username me --admin-password secret123 --user-password pass12345
```

| What | Details |
|---|---|
| Catalog | 4 categories, 17 products. Stock is chosen with `random.Random(42)` (0, 3, 10, 25 or 50), so it is the same every run; `stock=0` is handy for `in_stock=false` |
| Admin | `admin` / `admin12345` |
| Test users | `user1` and `user2`, password `user12345`, with phone, address and birth date filled in |
| Basket | `user1` has a basket with 3 items and no orders (try update/delete, then purchase) |
| Orders | `user2` has one `paid`, one `failed` and one `pending` order |

Seeded orders follow the same stock rules as the real flow: pending and paid
orders take their stock, a failed order does not. The command is idempotent:
existing users are kept, and baskets/orders are only created when the user has
none. No `Payment` rows are seeded, since an authority has to come from the real
Zarinpal sandbox. To test payment, use `user1` (basket -> purchase -> pay -> verify)
or pay `user2`'s `pending` order.

## Zarinpal sandbox

`ZARINPAL_SANDBOX=1` (the default) sends every request to
`https://sandbox.zarinpal.com`; set it to `0` to use `https://payment.zarinpal.com`.
No money is moved in the sandbox:

- `ZARINPAL_MERCHANT_ID` can be any valid random UUID v4 (a default is provided).
- Every authority returned by the sandbox starts with `S`.
- Open the returned `payment_url` in a browser; Zarinpal then redirects to
  `ZARINPAL_CALLBACK_URL` (`/api/payments/verify/`) with `Authority` and `Status`.

## Endpoints

Authenticated requests send the header `Authorization: Token <token>`.

| Method | URL | Notes |
|---|---|---|
| POST | `/api/auth/signup/` | `username, email, password, password2` -> token |
| POST | `/api/auth/signin/` | `username, password` -> token |
| POST | `/api/auth/signout/` | deletes the token |
| GET / PUT / PATCH / DELETE | `/api/profile/` | current user's profile (DELETE removes the account) |
| GET | `/api/products/` | list; `?search= &category= &category_slug= &min_price= &max_price= &in_stock= &ordering=` |
| GET | `/api/products/<id>/` | product detail |
| POST / PUT / PATCH / DELETE | `/api/products/...` | staff only |
| GET | `/api/categories/` | category list |
| GET / DELETE | `/api/basket/` | show / empty basket |
| POST | `/api/basket/items/` | `product_id, quantity` |
| PATCH / DELETE | `/api/basket/items/<id>/` | change quantity / remove item |
| GET / POST | `/api/orders/` | my orders / purchase (creates order from basket) |
| GET | `/api/orders/<id>/` | order detail |
| POST | `/api/orders/<id>/pay/` | returns `payment_url` (Zarinpal sandbox) |
| GET | `/api/payments/verify/` | Zarinpal callback (`Authority`, `Status`) |

## Purchase flow

1. `POST /api/basket/items/` to fill the basket.
2. `POST /api/orders/` creates a pending order and reserves the stock.
3. `POST /api/orders/<id>/pay/` returns `payment_url`; open it in a browser.
4. Zarinpal redirects to `/api/payments/verify/`. On success the order becomes
   `paid` and the basket is emptied; on failure the order becomes `failed` and the
   reserved stock is released.

Prices are stored in Toman; they are multiplied by 10 for Zarinpal (Rial).

## Git flow

- `main`: released versions only (tagged)
- `develop`: integration branch
- `feature/*`: one branch per feature, merged into `develop` with `--no-ff`
- `release/*`: release preparation, merged into `main` and back into `develop`
