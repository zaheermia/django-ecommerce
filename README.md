# Django eCommerce Application

An online shop made with Django and MariaDB. Vendors sell products in their
stores and buyers buy them and leave reviews.

Part 2 adds an API and a page that shows posts from Reddit.

## What you need
- Python 3.12 or newer
- Git
- MariaDB (running on your computer)

## How to run

1. Clone the project and go into its folder:
   ```
   git clone https://github.com/zaheermia/django-ecommerce.git
   cd django-ecommerce
   ```

2. Make a virtual environment and turn it on:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
   On Windows use `venv\Scripts\activate` instead.

3. Install the packages:
   ```
   pip install -r requirements.txt
   ```

4. Make the database. Open MariaDB:
   ```
   mysql -u root -p
   ```
   Then run these SQL commands (pick your own password):
   ```sql
   CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4;
   CREATE USER 'ecommerce_user'@'localhost' IDENTIFIED BY 'your-password';
   GRANT ALL PRIVILEGES ON ecommerce_db.* TO 'ecommerce_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

5. Make a `.env` file next to `manage.py` with the database details from step 4:
   ```
   SECRET_KEY=any-long-random-text
   DB_NAME=ecommerce_db
   DB_USER=ecommerce_user
   DB_PASSWORD=your-password
   ```

6. Migrate and run:
   ```
   python manage.py migrate
   python manage.py runserver
   ```

7. Go to http://127.0.0.1:8000/

Emails (invoices and password reset links) get printed in the terminal.

**Note about Django versions:** the email setting in `settings.py` uses
`MAILERS`, which only works in Django 6.1 or newer. `requirements.txt`
installs Django 6.1.3, so this works if you follow the steps above. On an
older Django version, delete the `MAILERS` setting and use this instead:
```
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

## Using the site

### Vendors
- **My Stores** - create, edit and delete stores, and add products to a store
- **My Products** - see all your products, add new ones, and edit or delete them
- **Reviews** - see every review for your products with a summary (total, average rating, verified and unverified) and the average for each product

### Buyers
- **Vendors**, **Stores** and **Products** - browse what's for sale
- **Cart** - add products and checkout, then the invoice is emailed
- **My Reviews** - see your reviews with a summary, and edit or delete them

## API

You have to log in with Basic Auth (I used Postman). It sends back JSON, or
XML if you add `?format=xml` to the URL.

| Method | URL | What it does |
|---|---|---|
| GET | `/api/stores/` | see all stores |
| POST | `/api/stores/` | vendor makes a store |
| GET | `/api/vendors/<id>/stores/` | see a vendor's stores |
| GET | `/api/stores/<id>/products/` | see a store's products |
| POST | `/api/stores/<id>/products/` | vendor adds a product |
| GET | `/api/stores/<id>/reviews/` | vendor sees the store's reviews |

## Planning

The `Planning` folder has the use case diagram, the sequence diagrams, the
class diagram, the CRUD matrix and my planning notes.

## Reddit

`/reddit/` shows posts from r/django. The code is in `ecommerce/functions/reddit.py`.

Reddit is blocking the request right now and sends back a `403` error, so the
page shows an error message instead. I followed the steps in the task and also
tried other subreddits but they all gave the same error. The screenshots are in
the `Screenshots` folder.
