"""URL patterns for the eCommerce app."""
from django.urls import path
from . import views, api_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path(
        'reset-password/<str:token>/',
        views.reset_password,
        name='reset_password',
    ),

    # vendors, stores and products everyone can see
    path('vendors/', views.vendor_list, name='vendor_list'),
    path(
        'vendors/<int:vendor_id>/',
        views.vendor_detail,
        name='vendor_detail',
    ),
    path('stores/', views.store_list, name='store_list'),
    path('products/', views.product_list, name='product_list'),
    path('stores/<int:store_id>/', views.store_detail, name='store_detail'),
    path(
        'products/<int:product_id>/',
        views.product_detail,
        name='product_detail',
    ),

    # vendor pages
    path('my-stores/', views.my_stores, name='my_stores'),
    path('my-stores/add/', views.add_store, name='add_store'),
    path('my-products/', views.my_products, name='my_products'),
    path(
        'my-stores/<int:store_id>/edit/',
        views.edit_store,
        name='edit_store',
    ),
    path(
        'my-stores/<int:store_id>/delete/',
        views.delete_store,
        name='delete_store',
    ),
    path(
        'my-stores/<int:store_id>/add-product/',
        views.add_product,
        name='add_product',
    ),
    path(
        'products/<int:product_id>/edit/',
        views.edit_product,
        name='edit_product',
    ),
    path(
        'products/<int:product_id>/delete/',
        views.delete_product,
        name='delete_product',
    ),

    # cart and checkout (buyers)
    path('cart/', views.view_cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path(
        'cart/update/<int:product_id>/',
        views.update_cart,
        name='update_cart',
    ),
    path(
        'cart/remove/<int:product_id>/',
        views.remove_from_cart,
        name='remove_from_cart',
    ),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),

    # reviews
    path(
        'products/<int:product_id>/review/',
        views.add_review,
        name='add_review',
    ),
    path('reviews/', views.review_list, name='review_list'),
    path(
        'reviews/<int:review_id>/edit/',
        views.edit_review,
        name='edit_review',
    ),
    path(
        'reviews/<int:review_id>/delete/',
        views.delete_review,
        name='delete_review',
    ),

    # Reddit feed
    path('reddit/', views.reddit_feed, name='reddit_feed'),

    # API (sends JSON, add ?format=xml to get XML)
    path('api/stores/', api_views.stores, name='api_stores'),
    path(
        'api/vendors/<int:vendor_id>/stores/',
        api_views.vendor_stores,
        name='api_vendor_stores',
    ),
    path(
        'api/stores/<int:store_id>/products/',
        api_views.store_products,
        name='api_store_products',
    ),
    path(
        'api/stores/<int:store_id>/reviews/',
        api_views.store_reviews,
        name='api_store_reviews',
    ),
]
