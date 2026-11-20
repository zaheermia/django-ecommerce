# Requirements

## Users
- **Vendors** - sell things in their own stores
- **Buyers** - buy things and leave reviews
- **Admin** - me, using the admin page

## Use cases
These match `Use Case Diagram.png` and the sequence diagrams.

### Vendor
- Create Store
- View Store
- Edit Store
- Delete Store
- Create Product
- View Product
- Edit Product
- Delete Product
- View Review
- View All Reviews

### Buyer
- View Vendors
- View Store
- View Product
- Create Review
- View Review
- Edit Review
- Delete Review

## Other things the app does
- Register and log in as a vendor or a buyer
- Buyers add products to a cart, checkout and get an invoice by email
- Reviews are verified if the buyer bought the product
- Forgot password link that stops working after 5 minutes
- Reddit page that shows posts from r/django
- REST API for stores, products and reviews
- MariaDB database
