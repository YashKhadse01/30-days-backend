# Django E-Commerce Backend with Stripe Integration

A RESTful e-commerce backend built using **Django, Django REST Framework, PostgreSQL, and Stripe**. The project demonstrates product management, authenticated shopping carts, transactional order processing, inventory reservation, and secure payment integration.

Developed as part of **Day 25 of the 30-Day Python Backend Development Roadmap**.

## 1. Project Overview

This project implements the backend services required for a basic e-commerce application.

Its primary objective is to demonstrate reliable order processing and secure payment handling using production-minded backend engineering practices.

### Core Features

- Public product listing and product details
- Admin-restricted product creation
- User-specific shopping carts
- Cart item addition, quantity updates, and deletion
- Transactional order creation
- PostgreSQL row-level locking for inventory operations
- Inventory reservation and restoration
- Stripe-hosted Checkout integration
- Stripe webhook signature verification
- Idempotent payment and order state transitions
- Automated API, payment, and concurrency testing

## 2. Technology Stack

| Category | Technology |
|---|---|
| Programming language | Python 3.11+ |
| Backend framework | Django |
| REST API framework | Django REST Framework |
| Database | PostgreSQL |
| Database driver | Psycopg 3 |
| Payment gateway | Stripe |
| Environment configuration | python-dotenv |
| Package management | uv |
| Testing | pytest, pytest-django, pytest-cov |
| Code linting | Ruff |
| Version control | Git and GitHub |

Dependency versions are managed through `pyproject.toml` and `uv.lock`.

## 3. Project Structure

```text
django_ecommerce_stripe/
├── cart/
├── config/
├── orders/
├── payments/
├── products/
├── tests/
│   ├── test_cart.py
│   ├── test_inventory_concurrency.py
│   ├── test_order_lifecycle.py
│   ├── test_stripe_checkout.py
│   └── test_stripe_webhook.py
├── .env.example
├── .gitignore
├── manage.py
├── pyproject.toml
├── uv.lock
└── README.md
```

### Application Responsibilities

**Products:** Manages the product catalog and provides public product retrieval with admin-controlled product creation.

**Cart:** Manages authenticated users' shopping carts, including item quantities and cart totals.

**Orders:** Converts shopping carts into orders, manages inventory reservations, and maintains order lifecycle transitions.

**Payments:** Integrates Stripe Checkout and processes verified payment events.

**Config:** Contains Django project settings and URL configuration.

**Tests:** Contains automated tests for cart operations, inventory concurrency, order lifecycle, and Stripe integration.

## 4. API Endpoints

### Product APIs

| Method | Endpoint | Access |
|---|---|---|
| GET | `/api/products/` | Public |
| POST | `/api/products/` | Admin |
| GET | `/api/products/{id}/` | Public |

Only active products are returned by the product APIs.

### Shopping Cart APIs

| Method | Endpoint | Access |
|---|---|---|
| GET | `/api/cart/` | Authenticated |
| POST | `/api/cart/items/` | Authenticated |
| PATCH | `/api/cart/items/{id}/` | Authenticated |
| DELETE | `/api/cart/items/{id}/` | Authenticated |

Cart operations are restricted to the authenticated user's cart.

### Order APIs

| Method | Endpoint | Access |
|---|---|---|
| GET | `/api/orders/` | Authenticated |
| GET | `/api/orders/{id}/` | Authenticated |
| POST | `/api/orders/checkout/` | Authenticated |

The order checkout endpoint creates an order from the authenticated user's cart.

Possible checkout responses include:

- `201 Created` — Order created successfully
- `400 Bad Request` — Empty cart or other checkout validation error
- `409 Conflict` — Insufficient inventory

### Payment APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/payments/checkout/` | Create or reuse a Stripe Checkout Session |
| POST | `/api/payments/webhook/` | Process signed Stripe payment events |

The payment checkout endpoint requires authentication.

The webhook endpoint verifies Stripe's signature rather than relying on customer authentication.

### Django Administration

```text
/admin/
```

The Django administration interface is available for authorized administrative users.

## 5. Local Development Setup

### Prerequisites

Install the following:

- Python 3.11 or newer
- PostgreSQL
- uv package manager
- Git

A Stripe test-mode account is required to exercise the Stripe payment integration.

### Step 1 — Open the Project Directory

From the repository root:

```powershell
cd day25\django_ecommerce_stripe
```

### Step 2 — Install Dependencies

```powershell
uv sync
```

This installs the project dependencies using the configured dependency groups and lockfile.

### Step 3 — Configure PostgreSQL

Create a PostgreSQL database and a database user with the required permissions.

For example, the local development database may be named:

```text
day25_ecommerce_db
```

Use the database credentials you configured locally.

### Step 4 — Configure Environment Variables

Create a `.env` file in the project directory.

Example configuration:

```dotenv
DJANGO_SECRET_KEY=replace-with-a-generated-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=day25_ecommerce_db
DB_USER=your_database_username
DB_PASSWORD=your_database_password
DB_HOST=127.0.0.1
DB_PORT=5432

STRIPE_SECRET_KEY=your_stripe_test_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_test_webhook_secret
```

These values are illustrative placeholders, not actual credentials.

**Security:** Never commit `.env`, database passwords, Django secret keys, or Stripe API credentials to GitHub.

### Step 5 — Apply Database Migrations

```powershell
uv run python manage.py migrate
```

### Step 6 — Start the Development Server

```powershell
uv run python manage.py runserver 8001
```

The local API will be available at:

```text
http://127.0.0.1:8001/
```

Example product endpoint:

```text
http://127.0.0.1:8001/api/products/
```

## 6. Order Processing Workflow

The application separates order creation from payment processing.

1. An authenticated user adds products to their cart.
2. The user initiates order checkout.
3. The backend validates the cart and available inventory.
4. A database transaction reserves the required stock.
5. An order is created.
6. The user initiates Stripe Checkout for that order.
7. Stripe processes the payment through its hosted Checkout page.
8. A verified Stripe webhook updates the order lifecycle.

### Inventory Consistency

The order service uses PostgreSQL transactions and row-level locking through `select_for_update()`.

This helps prevent concurrent checkout operations from reserving more inventory than is available.

### Order Lifecycle

The implemented lifecycle supports payment confirmation and order cancellation or expiration.

Stock restoration is designed to occur only once when the applicable cancellation or expiration transition takes place.

## 7. Stripe Payment Integration

Stripe Checkout provides a hosted payment interface.

The backend creates Checkout Sessions and associates them with existing orders.

### Checkout Session Handling

The payment service includes:

- Stripe API integration
- Checkout Session creation
- Reuse of eligible existing Checkout Sessions
- Rejection of expired sessions
- Idempotency keys for Checkout Session creation

### Supported Webhook Events

| Stripe event | Application behavior |
|---|---|
| `checkout.session.completed` | Processes the completed checkout event |
| `checkout.session.async_payment_succeeded` | Processes successful asynchronous payment |
| `checkout.session.async_payment_failed` | Handles asynchronous payment failure without marking the order paid |
| `checkout.session.expired` | Handles expiration and applicable inventory restoration |

Payment confirmation is based on verified Stripe event processing, not merely on a customer's return to a success URL.

### Webhook Security

The webhook implementation validates:

- Stripe webhook signature
- Associated order
- Checkout Session identity
- Payment amount
- Payment currency

It also includes safeguards against repeated processing of the same order transition.

### Local Stripe Testing

Use Stripe's test environment and a webhook forwarding mechanism configured for:

```text
http://127.0.0.1:8001/api/payments/webhook/
```

Configure the corresponding test webhook signing secret in your local environment.

Do not use live Stripe credentials for development testing.

## 8. Authentication and Authorization

The project uses Django REST Framework permission classes.

### Public Access

Unauthenticated users can retrieve active product listings and product details.

### Admin Access

Creating products requires administrative permissions through `IsAdminUser`.

### Authenticated Customer Access

Cart, order, and payment checkout operations require authenticated users.

Order queries are filtered by the authenticated user, and cart item operations enforce ownership checks.

The exact authentication mechanism depends on the Django REST Framework configuration in `config/settings.py`.

## 9. Testing and Quality Assurance

The project includes automated tests covering:

- Shopping cart behavior
- Concurrent inventory operations
- Order lifecycle transitions
- Stripe Checkout Session integration
- Stripe webhook verification and handling

### Run Automated Tests

```powershell
uv run python -m pytest tests/ -v --reuse-db
```

**Last verified result: 33 tests passed.**

### Run Ruff Linting

```powershell
uv run ruff check .
```

Last verified result:

```text
All checks passed!
```

### Run Django System Checks

```powershell
uv run python manage.py check
```

Last verified result:

```text
System check identified no issues (0 silenced).
```

### Optional Test Coverage

```powershell
uv run python -m pytest tests/ --cov=cart --cov=orders --cov=payments --cov=products --cov-report=term-missing
```

No specific coverage percentage is claimed without a measured coverage report.

## 10. Security and Reliability Considerations

The implementation includes several important backend safeguards.

**Environment-based configuration:** Sensitive credentials are loaded from environment variables rather than embedded in application code.

**Authorization:** User-specific resources are restricted to their owners.

**Transactional inventory management:** Database transactions and row locks protect stock updates during concurrent operations.

**Verified payment events:** Stripe webhook signatures and payment details are validated before applicable order transitions.

**Idempotent processing:** Payment and inventory transitions are designed to avoid repeated side effects.

**Administrative restrictions:** Product creation is restricted to administrative users.

These measures improve reliability but do not, by themselves, establish production readiness.

## 11. Known Limitations

This project is a backend learning and portfolio implementation rather than a fully deployed commercial e-commerce platform.

One known operational limitation is that an order may retain reserved inventory if the required Stripe expiration webhook is never received.

A future reconciliation mechanism could periodically check pending payment sessions and resolve stale reservations safely.

Additional deployment-specific configuration, monitoring, and security review would be necessary before production use.

## 12. Learning Outcomes

This project provides practical experience with:

- Designing RESTful APIs using Django REST Framework
- Managing relational data using PostgreSQL
- Implementing user-specific business operations
- Building transactional order processing
- Handling inventory concurrency
- Integrating an external payment provider
- Verifying signed webhook events
- Designing idempotent business workflows
- Writing automated backend tests
- Maintaining a structured Python project using uv
- Performing linting and Django configuration checks

## 13. Real-World Applications

The concepts demonstrated here can support backend systems for:

- Online retail stores
- Inventory-aware ordering platforms
- Digital commerce applications
- Business-to-customer ordering services
- Payment-enabled business platforms

## 14. Project Status

**Day 25 implementation: Completed and locally verified.**

Validation summary:

- 33 automated tests passed
- Ruff linting passed
- Django system checks passed
- PostgreSQL integration tested
- Stripe test-mode integration implemented
- Git ignore rules checked for local secrets and virtual environments

The project is ready for documentation review and repository preparation.

---

**Project:** Django E-Commerce Backend with Stripe Integration  
**Roadmap:** 30-Day Python Backend Development  
**Day:** 25  
**Status:** Local implementation and verification complete