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
- `seed_data` management command for demo data

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations accounts products orders
python manage.py migrate
python manage.py seed_data         # demo catalog + admin user (admin / admin12345)
python manage.py runserver
```

Optional environment variables: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`,
`ZARINPAL_MERCHANT_ID`, `ZARINPAL_CALLBACK_URL`, `ZARINPAL_SANDBOX` (default `1`).

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
