#!/bin/bash

# Create directories
mkdir -p ./{accounts,products,pages,payments,config}/management/commands

# Create files
touch ./accounts/management/commands/seed_users.py
touch ./products/management/commands/seed_products.py
touch ./pages/management/commands/seed_contact.py
touch ./payments/management/commands/seed_orders.py
touch ./config/management/commands/seed_all.py
