# Security

## Website
- Passwords are hashed by Django
- Users go in a Vendors or Buyers group when they register
- `@login_required` and `has_perm()` lock the pages
- Vendors can only change their own stores and products
- Buyers can only change their own reviews
- Delete pages ask "are you sure" first
- `{% csrf_token %}` in all forms
- Passwords and the secret key are in the `.env` file

## API
- You have to log in with Basic Auth for every request
- Only vendors can make stores
- Vendors can only add products to their own stores
- Vendors can only see reviews for their own stores
