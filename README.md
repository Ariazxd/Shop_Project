# Shop API

A Django REST Framework shop backend. API only, no templates / no frontend.

## Features

- Sign up / sign in / sign out (token authentication) and JWT login with refresh
- Interactive API docs: Swagger UI and ReDoc (drf-yasg)
- All endpoints are versioned under `/api/v1/`
- Profile: detail, update, delete (no list endpoint)
- Products: list, detail, create, update, delete (write access: staff only)
- Search, filter and ordering on the product list
- Favorites (add, remove and list favorite products)
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
python manage.py migrate     # after pulling a new model, run both commands again
python manage.py seed_data         # demo data, see "Demo data" below
python manage.py runserver
```

Then open <http://127.0.0.1:8000/swagger/> (or `/redoc/`) for the API docs. The raw
OpenAPI schema is at `/swagger.json` (or `/swagger.yaml`).

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
| Favorites | `user1` has 3 favorite products |
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
  `ZARINPAL_CALLBACK_URL` (`/api/v1/payments/verify/`) with `Authority` and `Status`.

## Endpoints

Authenticated requests send one of these headers:

- `Authorization: Bearer <access>`: JWT from `/api/v1/auth/token/` (access lives 30 minutes,
  refresh 7 days)
- `Authorization: Token <token>`: the token returned by signup / signin

| Method | URL | Notes |
|---|---|---|
| POST | `/api/v1/auth/signup/` | `username, email, password, password2` -> token |
| POST | `/api/v1/auth/signin/` | `username, password` -> token |
| POST | `/api/v1/auth/signout/` | deletes the token |
| POST | `/api/v1/auth/token/` | `username, password` -> JWT `access` and `refresh` |
| POST | `/api/v1/auth/token/refresh/` | `refresh` -> new `access` |
| GET / PUT / PATCH / DELETE | `/api/v1/profile/` | current user's profile (DELETE removes the account) |
| GET | `/api/v1/products/` | list; `?search= &category= &category_slug= &min_price= &max_price= &in_stock= &ordering=` |
| GET | `/api/v1/products/<id>/` | product detail |
| POST / PUT / PATCH / DELETE | `/api/v1/products/...` | staff only |
| GET | `/api/v1/categories/` | category list |
| POST / DELETE | `/api/v1/products/<id>/favorite/` | add / remove a favorite (login required) |
| GET | `/api/v1/favorites/` | my favorite products, newest first |
| GET / DELETE | `/api/v1/basket/` | show / empty basket |
| POST | `/api/v1/basket/items/` | `product_id, quantity` |
| PATCH / DELETE | `/api/v1/basket/items/<id>/` | change quantity / remove item |
| GET / POST | `/api/v1/orders/` | my orders / purchase (creates order from basket) |
| GET | `/api/v1/orders/<id>/` | order detail |
| POST | `/api/v1/orders/<id>/pay/` | returns `payment_url` (Zarinpal sandbox) |
| GET | `/api/v1/payments/verify/` | Zarinpal callback (`Authority`, `Status`) |

## Purchase flow

1. `POST /api/v1/basket/items/` to fill the basket.
2. `POST /api/v1/orders/` creates a pending order and reserves the stock.
3. `POST /api/v1/orders/<id>/pay/` returns `payment_url`; open it in a browser.
4. Zarinpal redirects to `/api/v1/payments/verify/`. On success the order becomes
   `paid` and the basket is emptied; on failure the order becomes `failed` and the
   reserved stock is released.

If you override `ZARINPAL_CALLBACK_URL`, it must now point to `/api/v1/payments/verify/`.

Prices are stored in Toman; they are multiplied by 10 for Zarinpal (Rial).

## Project layout

Every app keeps its models, admin and signals at the top and all of its API code
in an `api/` package:

```
accounts/   models.py  admin.py  signals.py  api/{serializers,views,urls}.py
products/   models.py  admin.py  api/{serializers,views,urls,permissions,filters}.py
orders/     models.py  admin.py  zarinpal.py  api/{serializers,views,payment_views,urls}.py
shop/       settings.py  urls.py   (includes accounts.api.urls, products.api.urls, orders.api.urls)
```

## Git flow

- `main`: released versions only (tagged)
- `develop`: integration branch
- `feature/*`: one branch per feature, merged into `develop` with `--no-ff`
- `release/*`: release preparation, merged into `main` and back into `develop`
