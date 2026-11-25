# Boutique OS — Project Map

Where to find things, and where to change them. Read this first.

## Run it

```bash
# Backend (terminal 1)
cd services/api && source .venv/bin/activate
python manage.py runserver          # API on http://127.0.0.1:8000

# Frontend (terminal 2, from the repository root)
npm run dev                         # app on http://localhost:5173
```

## Frontend: `apps/web/src/`

Rule: **one file, one job.** If you want to change something, the table tells you which file.

| I want to change… | Open this file |
| --- | --- |
| Which page is shown / what is shared between pages | `App.jsx` |
| The left menu | `layouts/Sidebar.jsx` |
| The shop areas and compartments (A01, B02…) | `data/shopAreas.js` |
| The demo products and prices | `data/sampleProducts.js` |
| How money is displayed (1,800 RWF) | `utils/formatMoney.js` |
| The main selling screen (header + layout) | `features/digital-shop/DigitalShopPage.jsx` |
| The row of shop areas | `features/digital-shop/AreaPicker.jsx` |
| Compartments, search box, product cards | `features/digital-shop/ProductPanel.jsx` |
| Which products are shown (search vs. location) | `features/digital-shop/useShopBrowser.js` |
| Basket rules (add, quantity, totals) | `features/basket/useBasket.js` |
| How the basket looks | `features/basket/BasketPanel.jsx` |
| Payment rules (change, credit, errors) | `features/checkout/useCheckout.js` |
| The payment methods offered | `features/checkout/paymentMethods.js` |
| The payment form | `features/checkout/PaymentStep.jsx` |
| The receipt | `features/checkout/ReceiptStep.jsx` |
| The window that holds payment + receipt | `features/checkout/CheckoutModal.jsx` |
| The Sales History page | `features/sales/SalesHistoryPage.jsx` |

### Two kinds of files

- **`use…js` files (hooks)** hold *logic and state*: numbers, rules, what happens on a click.
- **`.jsx` files (components)** hold *what the screen looks like*. They receive data and report clicks.

When you explain a feature, explain the hook first (the rules), then the component (the picture).

### Styles: `styles/`

Numbered in the order they load. Order matters, because later rules can override earlier ones.

| File | Covers |
| --- | --- |
| `base.css` | Page font, colours, global defaults |
| `01-sidebar.css` | App shell and left menu |
| `02-topbar-areas.css` | Header, section headings, shop-area buttons |
| `03-digital-shop.css` | Compartments, search, product grid |
| `04-basket.css` | Basket panel |
| `05-responsive.css` | Tablet and phone layout changes |
| `06-checkout-receipt.css` | Checkout window and receipt |
| `07-small-screen-print.css` | Very small screens and receipt printing |
| `index.css` | Imports the files above in order |

### Not connected yet

The frontend still uses demo data (`data/`) and does not call the backend. The backend already
has `POST /api/businesses/<id>/sales/confirm/`; connecting it is the next step after the redesign.

## Backend: `services/api/`

| File | Job |
| --- | --- |
| `config/settings.py` | Project settings (apps, database, security) |
| `config/urls.py` | Top-level routes: `/admin/` and `/api/` |
| `core/models.py` | Database tables |
| `core/serializers.py` | Turns database objects into JSON and checks input |
| `core/services.py` | Business logic, including `confirm_sale()` |
| `core/views.py` | Receives API requests |
| `core/urls.py` | Routes API paths to views |
| `core/admin.py` | Django Admin screens |
| `core/migrations/` | Database history. Never delete. |
| `core/tests.py` | Automated tests |

## Things to check in your own repository

These were found in the uploaded copy. Check them locally before acting.

- **`services/api/app/main.py` is empty (0 bytes)** and nothing imports it. It looks like an abandoned
  experiment. Confirm with `grep -r "app.main" services/api` and, if nothing appears, remove it with `git rm`.
- **`services/api/pyproject.toml` is empty.** Dependencies are actually listed in `requirements.txt`.
- **Every file in `docs/` is empty**, and so are `LICENSE`, `CONTRIBUTING.md`, `.editorconfig`.
- **The uploaded `.gitignore` was empty.** If yours is too, `node_modules/`, `.venv/`, `db.sqlite3` and
  `.env` can be committed by accident. Suggested contents:

```gitignore
node_modules/
dist/
.venv/
__pycache__/
*.pyc
.env
.env.*
services/api/db.sqlite3
```

Your report says `.gitignore` has a staged change locally, so compare it with this list instead of replacing it.

## History

`docs/refactor/original-frontend/` keeps the original single-file `App.jsx`, `App.css` and `index.css`
for comparison. Nothing imports them. Delete the folder once you are happy with the new structure.
