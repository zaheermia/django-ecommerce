"""Views for the eCommerce app."""
import secrets
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from hashlib import sha1

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.core.mail import EmailMessage
from django.db.models import Avg, Count

from .models import Store, Product, Order, OrderItem, Review, ResetToken
from .functions.reddit import get_reddit_posts


def setup_groups():
    """Make the Vendors and Buyers groups and give them their permissions."""
    vendors, created = Group.objects.get_or_create(name='Vendors')
    vendor_perms = Permission.objects.filter(
        content_type__app_label='ecommerce',
        codename__in=[
            'add_store', 'change_store', 'delete_store', 'view_store',
            'add_product', 'change_product', 'delete_product',
            'view_product', 'view_review',
        ]
    )
    vendors.permissions.set(vendor_perms)

    buyers, created = Group.objects.get_or_create(name='Buyers')
    buyer_perms = Permission.objects.filter(
        content_type__app_label='ecommerce',
        codename__in=[
            'view_store', 'view_product',
            'add_order', 'view_order',
            'add_review', 'change_review', 'delete_review', 'view_review',
        ]
    )
    buyers.permissions.set(buyer_perms)

    return vendors, buyers


def home(request):
    """Show the home page with links to the main parts of the site."""
    return render(request, 'ecommerce/home.html')


def register_user(request):
    """Register a new vendor or buyer and log them in."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        account_type = request.POST.get('account_type')

        # check everything was filled in properly
        error = None
        if not username or not email or not password:
            error = 'Please fill in all the fields.'
        elif account_type not in ['buyer', 'vendor']:
            error = 'Please choose buyer or vendor.'
        elif password != password2:
            error = "The passwords don't match."
        elif User.objects.filter(username=username).exists():
            error = 'That username is already taken.'
        elif User.objects.filter(email=email).exists():
            error = 'That email is already being used.'
        else:
            # use Django's password rules (length, not too common etc.)
            try:
                validate_password(password)
            except ValidationError as e:
                error = ' '.join(e.messages)

        if error:
            return render(request, 'ecommerce/register.html', {
                'error': error,
                'username': username,
                'email': email,
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        # put the user in the right group
        vendors, buyers = setup_groups()
        if account_type == 'vendor':
            user.groups.add(vendors)
        else:
            user.groups.add(buyers)
        user.save()

        login(request, user)
        messages.success(
            request,
            f'Welcome {username}, your account was made!',
        )
        return redirect('home')

    return render(request, 'ecommerce/register.html')


def login_user(request):
    """Log a user in with their username and password."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # keep anything that was in the session (like the cart)
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'ecommerce/login.html', {
                'error': 'Invalid username or password.',
            })

    return render(request, 'ecommerce/login.html')


def logout_user(request):
    """Log the user out and go back to the login page."""
    logout(request)
    return redirect('login')


# ---------- Stores and products that everyone can see ----------

def store_list(request):
    """Show all the stores."""
    stores = Store.objects.all()
    return render(request, 'ecommerce/store_list.html', {'stores': stores})


def store_detail(request, store_id):
    """Show one store and its products."""
    store = get_object_or_404(Store, id=store_id)
    products = Product.objects.filter(store=store)
    return render(
        request,
        'ecommerce/store_detail.html',
        {'store': store, 'products': products},
    )


def product_detail(request, product_id):
    """Show one product and its reviews."""
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product).order_by('-date')
    return render(request, 'ecommerce/product_detail.html', {
        'product': product,
        'reviews': reviews,
    })


def product_list(request):
    """Show all the products from every store."""
    products = Product.objects.all().order_by('name')
    return render(
        request,
        'ecommerce/product_list.html',
        {'products': products},
    )


def vendor_list(request):
    """Show all the vendors and how many stores each one has."""
    vendors = User.objects.filter(groups__name='Vendors').annotate(
        store_count=Count('store'),
    ).order_by('username')
    return render(request, 'ecommerce/vendor_list.html', {'vendors': vendors})


def vendor_detail(request, vendor_id):
    """Show one vendor and all of their stores."""
    vendor = get_object_or_404(User, id=vendor_id, groups__name='Vendors')
    stores = Store.objects.filter(vendor=vendor)
    return render(request, 'ecommerce/vendor_detail.html', {
        'vendor': vendor,
        'stores': stores,
    })


# ---------- Vendor pages ----------

@login_required
def my_stores(request):
    """Show the vendor's own stores."""
    if not request.user.has_perm('ecommerce.add_store'):
        return HttpResponseForbidden('Only vendors can see this page.')

    stores = Store.objects.filter(vendor=request.user)
    return render(request, 'ecommerce/my_stores.html', {'stores': stores})


@login_required
def add_store(request):
    """Let a vendor make a new store."""
    if not request.user.has_perm('ecommerce.add_store'):
        return HttpResponseForbidden('Only vendors can add stores.')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')

        if not name:
            return render(request, 'ecommerce/store_form.html', {
                'error': 'The store needs a name.',
                'description': description,
            })

        Store.objects.create(
            vendor=request.user,
            name=name,
            description=description,
        )
        messages.success(request, 'Store added.')
        return redirect('my_stores')

    return render(request, 'ecommerce/store_form.html')


@login_required
def edit_store(request, store_id):
    """Let a vendor change their store's name and description."""
    if not request.user.has_perm('ecommerce.change_store'):
        return HttpResponseForbidden('Only vendors can edit stores.')

    # vendor=request.user makes sure vendors can only edit their own stores
    store = get_object_or_404(Store, id=store_id, vendor=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')

        if not name:
            return render(request, 'ecommerce/store_form.html', {
                'store': store,
                'error': 'The store needs a name.',
            })

        store.name = name
        store.description = description
        store.save()
        messages.success(request, 'Store updated.')
        return redirect('my_stores')

    return render(request, 'ecommerce/store_form.html', {
        'store': store,
        'name': store.name,
        'description': store.description,
    })


@login_required
def delete_store(request, store_id):
    """Let a vendor delete their store after they confirm."""
    if not request.user.has_perm('ecommerce.delete_store'):
        return HttpResponseForbidden('Only vendors can delete stores.')

    store = get_object_or_404(Store, id=store_id, vendor=request.user)

    # only delete when they click the button on the "are you sure" page
    if request.method == 'POST':
        store.delete()
        messages.success(request, 'Store deleted.')
        return redirect('my_stores')

    return render(request, 'ecommerce/confirm_delete.html', {
        'thing': store,
        'back_url': reverse('my_stores'),
    })


@login_required
def my_products(request):
    """Show the vendor's products grouped by store."""
    if not request.user.has_perm('ecommerce.add_product'):
        return HttpResponseForbidden('Only vendors can see this page.')

    stores = Store.objects.filter(vendor=request.user)
    store_products = []
    for store in stores:
        store_products.append({
            'store': store,
            'products': Product.objects.filter(store=store),
        })
    return render(request, 'ecommerce/my_products.html', {
        'store_products': store_products,
    })


def get_product_info(request):
    """Get the product details from the form and check them."""
    name = request.POST.get('name')
    description = request.POST.get('description', '')
    price = request.POST.get('price')
    stock = request.POST.get('stock')
    info = {
        'name': name,
        'description': description,
        'price': price,
        'stock': stock,
    }

    if not name or not price or not stock:
        return info, 'Please fill in the name, price and stock.'

    try:
        info['price'] = Decimal(price)
        info['stock'] = int(stock)
    except (InvalidOperation, ValueError):
        return info, 'Price and stock have to be numbers.'

    if info['price'] < 0 or info['stock'] < 0:
        return info, "Price and stock can't be negative."

    return info, None


@login_required
def add_product(request, store_id):
    """Let a vendor add a product to one of their stores."""
    if not request.user.has_perm('ecommerce.add_product'):
        return HttpResponseForbidden('Only vendors can add products.')

    store = get_object_or_404(Store, id=store_id, vendor=request.user)

    if request.method == 'POST':
        info, error = get_product_info(request)
        if error:
            return render(request, 'ecommerce/product_form.html', {
                'store': store,
                'error': error,
                **info,
            })

        Product.objects.create(
            store=store,
            name=info['name'],
            description=info['description'],
            price=info['price'],
            stock=info['stock'],
        )
        messages.success(request, 'Product added.')
        return redirect('my_products')

    return render(request, 'ecommerce/product_form.html', {'store': store})


@login_required
def edit_product(request, product_id):
    """Let a vendor change one of their products."""
    if not request.user.has_perm('ecommerce.change_product'):
        return HttpResponseForbidden('Only vendors can edit products.')

    # store__vendor=request.user makes sure the product is in one of
    # their stores
    product = get_object_or_404(
        Product,
        id=product_id,
        store__vendor=request.user,
    )

    if request.method == 'POST':
        info, error = get_product_info(request)
        if error:
            return render(request, 'ecommerce/product_form.html', {
                'store': product.store,
                'product': product,
                'error': error,
                **info,
            })

        product.name = info['name']
        product.description = info['description']
        product.price = info['price']
        product.stock = info['stock']
        product.save()
        messages.success(request, 'Product updated.')
        return redirect('my_products')

    return render(request, 'ecommerce/product_form.html', {
        'store': product.store,
        'product': product,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
    })


@login_required
def delete_product(request, product_id):
    """Let a vendor delete their product after they confirm."""
    if not request.user.has_perm('ecommerce.delete_product'):
        return HttpResponseForbidden('Only vendors can delete products.')

    product = get_object_or_404(
        Product,
        id=product_id,
        store__vendor=request.user,
    )

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted.')
        return redirect('my_products')

    return render(request, 'ecommerce/confirm_delete.html', {
        'thing': product,
        'back_url': reverse('my_products'),
    })


# ---------- Cart (saved in the session) ----------
# The cart is a dictionary in the session like {'product_id': quantity}

def is_buyer(user):
    """Check if the user is a buyer."""
    return user.has_perm('ecommerce.add_order')


# gets the products in the cart and works out the total
def get_cart_items(request):
    """Get the products in the cart and work out the total."""
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for product_id, quantity in list(cart.items()):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            # the vendor deleted this product, so take it out of the cart
            del cart[product_id]
            continue

        subtotal = product.price * quantity
        total += subtotal
        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    request.session['cart'] = cart
    return items, total


@login_required
def add_to_cart(request, product_id):
    """Add a product to the buyer's cart in the session."""
    if not is_buyer(request.user):
        return HttpResponseForbidden('Only buyers can add things to a cart.')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity'))
            if quantity < 1:
                quantity = 1
        except (ValueError, TypeError):
            quantity = 1

        cart = request.session.get('cart', {})
        # session keys have to be strings
        key = str(product.id)
        new_quantity = cart.get(key, 0) + quantity

        if new_quantity > product.stock:
            new_quantity = product.stock
            messages.error(
                request,
                f'Sorry, there are only {product.stock} '
                f'{product.name} in stock.',
            )

        if new_quantity > 0:
            cart[key] = new_quantity
            messages.success(request, f'{product.name} added to your cart.')

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart')


@login_required
def update_cart(request, product_id):
    """Change how many of a product are in the cart."""
    if not is_buyer(request.user):
        return HttpResponseForbidden('Only buyers have a cart.')

    if request.method == 'POST':
        cart = request.session.get('cart', {})
        key = str(product_id)

        try:
            quantity = int(request.POST.get('quantity'))
        except (ValueError, TypeError):
            quantity = 1

        if key in cart:
            if quantity < 1:
                del cart[key]
            else:
                product = get_object_or_404(Product, id=product_id)
                cart[key] = min(quantity, product.stock)

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart')


@login_required
def remove_from_cart(request, product_id):
    """Take a product out of the cart."""
    if not is_buyer(request.user):
        return HttpResponseForbidden('Only buyers have a cart.')

    if request.method == 'POST':
        cart = request.session.get('cart', {})
        cart.pop(str(product_id), None)
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart')


@login_required
def view_cart(request):
    """Show the cart and the total."""
    if not is_buyer(request.user):
        return HttpResponseForbidden('Only buyers have a cart.')

    items, total = get_cart_items(request)
    return render(
        request,
        'ecommerce/cart.html',
        {'items': items, 'total': total},
    )


# ---------- Checkout and invoices ----------

# makes the invoice email
def build_invoice_email(order):
    """Make the invoice email for an order."""
    lines = [
        f"Hi {order.buyer.username},",
        "",
        "Thanks for your order! Here is your invoice:",
        "",
    ]
    lines.append(f"Order number: {order.id}")
    order_date = timezone.localtime(order.date)
    lines.append(
        f"Date: {order_date.strftime('%d %B %Y %H:%M')}"
    )
    lines.append("")

    for item in OrderItem.objects.filter(order=order):
        lines.append(
            f"{item.product_name} x {item.quantity} @ R{item.price} "
            f"= R{item.price * item.quantity}"
        )

    lines.append("")
    lines.append(f"Total: R{order.total}")

    subject = f"Your invoice for order {order.id}"
    body = "\n".join(lines)
    return EmailMessage(subject, body, "shop@example.com", [order.buyer.email])


@login_required
def checkout(request):
    """Make the order, update the stock and email the invoice."""
    if not is_buyer(request.user):
        return HttpResponseForbidden('Only buyers can checkout.')

    if request.method != 'POST':
        return redirect('cart')

    items, total = get_cart_items(request)

    if not items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    # make sure there is still enough stock before we make the order
    for item in items:
        if item['quantity'] > item['product'].stock:
            messages.error(
                request,
                f"Sorry, there are only {item['product'].stock} "
                f"{item['product'].name} left.",
            )
            return redirect('cart')

    # make the order (the invoice) and its items
    order = Order.objects.create(buyer=request.user, total=total)
    for item in items:
        product = item['product']
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            quantity=item['quantity'],
            price=product.price,
        )
        product.stock -= item['quantity']
        product.save()

    # empty the cart
    request.session['cart'] = {}
    request.session.modified = True

    # email the invoice
    try:
        build_invoice_email(order).send()
        messages.success(
            request,
            'Thanks for your order! The invoice was sent to your email.',
        )
    except Exception:
        messages.error(
            request,
            "Your order was placed but we couldn't send the invoice email.",
        )

    return redirect('order_detail', order_id=order.id)


@login_required
def my_orders(request):
    """Show the buyer's past orders."""
    if not is_buyer(request.user):
        return HttpResponseForbidden('Only buyers have orders.')

    orders = Order.objects.filter(buyer=request.user).order_by('-date')
    return render(request, 'ecommerce/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    # buyer=request.user so people can only see their own invoices
    """Show one of the buyer's orders (the invoice)."""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    items = OrderItem.objects.filter(order=order)
    return render(
        request,
        'ecommerce/order_detail.html',
        {'order': order, 'items': items},
    )


# ---------- Reviews ----------

@login_required
def add_review(request, product_id):
    """Let a buyer leave a review on a product."""
    if not request.user.has_perm('ecommerce.add_review'):
        return HttpResponseForbidden('Only buyers can leave reviews.')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        comment = request.POST.get('comment', '')

        try:
            rating = int(request.POST.get('rating'))
        except (ValueError, TypeError):
            rating = 0

        if rating < 1 or rating > 5:
            messages.error(request, 'The rating has to be between 1 and 5.')
            return redirect('product_detail', product_id=product.id)

        if not comment:
            messages.error(request, 'Please write a comment.')
            return redirect('product_detail', product_id=product.id)

        # If the buyer ordered this product, mark the review verified.
        bought_it = OrderItem.objects.filter(
            order__buyer=request.user,
            product=product,
        ).exists()

        Review.objects.create(
            product=product,
            buyer=request.user,
            rating=rating,
            comment=comment,
            verified=bought_it,
        )
        messages.success(request, 'Thanks for your review!')

    return redirect('product_detail', product_id=product.id)


@login_required
def review_list(request):
    """Show reviews with a summary.

    Vendors see the reviews for all their products. Buyers see the reviews
    they wrote and can edit or delete them.
    """
    if request.user.has_perm('ecommerce.add_store'):
        reviews = Review.objects.filter(product__store__vendor=request.user)
        products = Product.objects.filter(
            store__vendor=request.user,
        ).annotate(
            review_count=Count('review'),
            average=Avg('review__rating'),
        ).order_by('name')
        is_vendor = True
    elif request.user.has_perm('ecommerce.add_review'):
        reviews = Review.objects.filter(buyer=request.user)
        products = None
        is_vendor = False
    else:
        return HttpResponseForbidden('Only vendors and buyers have reviews.')

    stats = reviews.aggregate(total=Count('id'), average=Avg('rating'))
    stats['verified'] = reviews.filter(verified=True).count()
    stats['unverified'] = stats['total'] - stats['verified']

    return render(request, 'ecommerce/review_list.html', {
        'reviews': reviews.order_by('-date'),
        'products': products,
        'stats': stats,
        'is_vendor': is_vendor,
    })


@login_required
def edit_review(request, review_id):
    """Let a buyer change the rating and comment on their own review."""
    if not request.user.has_perm('ecommerce.add_review'):
        return HttpResponseForbidden('Only buyers can edit reviews.')

    # buyer=request.user so buyers can only edit their own reviews
    review = get_object_or_404(Review, id=review_id, buyer=request.user)

    if request.method == 'POST':
        comment = request.POST.get('comment', '')
        try:
            rating = int(request.POST.get('rating'))
        except (ValueError, TypeError):
            rating = 0

        error = None
        if rating < 1 or rating > 5:
            error = 'The rating has to be between 1 and 5.'
        elif not comment:
            error = 'Please write a comment.'

        if error:
            return render(request, 'ecommerce/review_form.html', {
                'review': review,
                'rating': rating,
                'comment': comment,
                'error': error,
            })

        review.rating = rating
        review.comment = comment
        review.save()
        messages.success(request, 'Review updated.')
        return redirect('review_list')

    return render(request, 'ecommerce/review_form.html', {
        'review': review,
        'rating': review.rating,
        'comment': review.comment,
    })


@login_required
def delete_review(request, review_id):
    """Let a buyer delete their own review after they confirm."""
    if not request.user.has_perm('ecommerce.add_review'):
        return HttpResponseForbidden('Only buyers can delete reviews.')

    review = get_object_or_404(Review, id=review_id, buyer=request.user)

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted.')
        return redirect('review_list')

    return render(request, 'ecommerce/confirm_delete.html', {
        'thing': f'your review of {review.product.name}',
        'back_url': reverse('review_list'),
    })


# ---------- Forgot password ----------

# makes a token and the reset link
def generate_reset_url(request, user):
    """Make a reset token and the reset password link."""
    token = secrets.token_urlsafe(16)
    expiry_date = timezone.now() + timedelta(minutes=5)

    # Only the hashed token gets saved, so the real link can't be worked out
    # from the database.
    ResetToken.objects.create(
        user=user,
        token=sha1(token.encode()).hexdigest(),
        expiry_date=expiry_date,
    )

    return request.build_absolute_uri(reverse('reset_password', args=[token]))


def build_reset_email(user, reset_url):
    """Make the email with the reset password link."""
    subject = "Password Reset"
    body = (
        f"Hi {user.username},\n\n"
        f"Here is your link to reset your password: {reset_url}\n\n"
        f"The link stops working after 5 minutes."
    )
    return EmailMessage(subject, body, "shop@example.com", [user.email])


def forgot_password(request):
    """Send a reset password link to the email entered."""
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if user is not None:
            url = generate_reset_url(request, user)
            try:
                build_reset_email(user, url).send()
            except Exception:
                messages.error(
                    request,
                    (
                        "Sorry, we couldn't send the email. "
                        "Please try again later."
                    ),
                )
                return redirect('forgot_password')

        # Same message either way so people can't find out which emails
        # have accounts.
        messages.success(
            request,
            'If that email has an account, a reset link has been sent to it.',
        )
        return redirect('login')

    return render(request, 'ecommerce/forgot_password.html')


def reset_password(request, token):
    """Let the user set a new password with a valid link."""
    hashed = sha1(token.encode()).hexdigest()
    reset_token = ResetToken.objects.filter(token=hashed, used=False).first()

    # check the token exists and hasn't expired
    if reset_token is None:
        return render(
            request,
            'ecommerce/reset_password.html',
            {'invalid': True},
        )

    if reset_token.expiry_date < timezone.now():
        reset_token.delete()
        return render(
            request,
            'ecommerce/reset_password.html',
            {'invalid': True},
        )

    if request.method == 'POST':
        password = request.POST.get('password')
        password_conf = request.POST.get('password_conf')

        if password != password_conf:
            return render(
                request,
                'ecommerce/reset_password.html',
                {'error': "The passwords don't match."},
            )

        try:
            validate_password(password, reset_token.user)
        except ValidationError as e:
            return render(
                request,
                'ecommerce/reset_password.html',
                {'error': ' '.join(e.messages)},
            )

        user = reset_token.user
        user.set_password(password)
        user.save()

        # delete the token so the link can't be used again
        reset_token.delete()

        messages.success(
            request,
            'Your password has been changed. You can log in now.',
        )
        return redirect('login')

    return render(request, 'ecommerce/reset_password.html')


# ---------- Reddit feed ----------

def reddit_feed(request):
    """Show the newest posts from r/django."""
    subreddit = "django"
    # get the posts from Reddit
    posts = get_reddit_posts(subreddit)
    # send the posts to the template
    return render(request, 'ecommerce/reddit_feed.html', {
        'posts': posts,
        'subreddit': subreddit,
    })
