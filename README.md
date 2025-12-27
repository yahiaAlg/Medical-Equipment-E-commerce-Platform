# Django Database Seeding Guide

## Directory Structure

Place each management command file in its respective app:

```
project/
├── accounts/
│   └── management/
│       └── commands/
│           └── seed_users.py
├── products/
│   └── management/
│       └── commands/
│           └── seed_products.py
├── pages/
│   └── management/
│       └── commands/
│           └── seed_contact.py
├── payments/
│   └── management/
│       └── commands/
│           └── seed_orders.py
└── config/
    └── management/
        └── commands/
            └── seed_all.py
```

**Note:** Create the `management/commands/` directories if they don't exist. Add empty `__init__.py` files in each directory.

## Required Dependencies

Add to `requirements.txt`:

```
requests>=2.31.0
Pillow>=10.0.0
```

Install:

```bash
pip install requests Pillow
```

## Usage

### Seed All Data (Recommended)

```bash
python manage.py seed_all
```

### Seed Individual Apps

```bash
# Seed users first (required for others)
python manage.py seed_users

# Seed products (includes image downloads)
python manage.py seed_products

# Seed contact data
python manage.py seed_contact

# Seed orders (requires users and products)
python manage.py seed_orders
```

## Demo Accounts

| Type         | Username      | Password   | Email             |
| ------------ | ------------- | ---------- | ----------------- |
| General User | demo_general  | demo123456 | general@demo.com  |
| Pharmacy     | demo_pharmacy | demo123456 | pharmacy@demo.com |
| Clinic Staff | demo_clinic   | demo123456 | clinic@demo.com   |
| Doctor       | demo_doctor   | demo123456 | doctor@demo.com   |

## What Gets Created

- **4 demo users** (one of each type with complete profiles)
- **8 product categories** (Diagnostic, Surgical, Monitoring, etc.)
- **8 brands** (MedTech Pro, HealthLine, etc.)
- **30 products** with specifications and pricing
- **90 product images** (3 per product, downloaded from Unsplash)
- **10 FAQs** across 5 categories
- **5 testimonials** from healthcare professionals
- **3 contact messages** (sample inquiries)
- **Carts** for all users with random items
- **3-9 sample orders** with complete order history

## Image Download Notes

Images are downloaded from Unsplash's source API (`https://source.unsplash.com`). This:

- Provides free, high-quality placeholder images
- Downloads automatically during seeding
- Requires internet connection
- May take a few minutes to complete

If image downloads fail, products will still be created without images.

## Troubleshooting

**Error: "No such table"**

```bash
python manage.py makemigrations
python manage.py migrate
```

**Error: "requests module not found"**

```bash
pip install requests
```

**Slow image downloads**

- Normal for first run (downloading 90 images)
- Run `seed_products` separately to monitor progress
- Consider reducing images per product in the seeder

**Re-running seeders**

- Commands use `get_or_create()` to avoid duplicates
- Safe to run multiple times
- To reset: delete database and run `migrate` + `seed_all`
