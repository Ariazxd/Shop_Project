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

## Git flow

- `main`: released versions only (tagged)
- `develop`: integration branch
- `feature/*`: one branch per feature, merged into `develop` with `--no-ff`
- `release/*`: release preparation, merged into `main` and back into `develop`
