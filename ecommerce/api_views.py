"""API views for the eCommerce app.

You have to be logged in to use these (Basic Auth in Postman).
They send back JSON, or XML if you add ?format=xml to the URL.
"""
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Store, Product, Review
from .serializers import StoreSerializer, ProductSerializer, ReviewSerializer

# Basic Auth for Postman, Session so it also works in the browser when
# you're logged in
AUTH_CLASSES = [BasicAuthentication, SessionAuthentication]


def is_vendor(user):
    """Check if the user is a vendor."""
    return user.has_perm('ecommerce.add_store')


@api_view(['GET', 'POST'])
@authentication_classes(AUTH_CLASSES)
@permission_classes([IsAuthenticated])
def stores(request):
    """GET shows all stores. POST lets a vendor make a new store."""
    if request.method == 'GET':
        serializer = StoreSerializer(Store.objects.all(), many=True)
        return Response(serializer.data)

    if not is_vendor(request.user):
        return Response(
            {'error': 'Only vendors can create stores.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = StoreSerializer(data=request.data)
    if serializer.is_valid():
        # the store always belongs to whoever is logged in
        serializer.save(vendor=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes(AUTH_CLASSES)
@permission_classes([IsAuthenticated])
def vendor_stores(request, vendor_id):
    """Show all the stores that belong to a vendor."""
    vendor = get_object_or_404(User, id=vendor_id)
    if not is_vendor(vendor):
        return Response(
            {'error': 'That user is not a vendor.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = StoreSerializer(
        Store.objects.filter(vendor=vendor),
        many=True,
    )
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@authentication_classes(AUTH_CLASSES)
@permission_classes([IsAuthenticated])
def store_products(request, store_id):
    """GET shows a store's products. POST lets the store's vendor add one."""
    store = get_object_or_404(Store, id=store_id)

    if request.method == 'GET':
        serializer = ProductSerializer(
            Product.objects.filter(store=store),
            many=True,
        )
        return Response(serializer.data)

    if not request.user.has_perm('ecommerce.add_product'):
        return Response(
            {'error': 'Only vendors can add products.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    if store.vendor != request.user:
        return Response(
            {'error': 'You can only add products to your own stores.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(store=store)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes(AUTH_CLASSES)
@permission_classes([IsAuthenticated])
def store_reviews(request, store_id):
    """Show the reviews for all the products in one of the vendor's stores."""
    store = get_object_or_404(Store, id=store_id)

    if store.vendor != request.user:
        return Response(
            {'error': 'You can only see reviews for your own stores.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    reviews = Review.objects.filter(product__store=store).order_by('-date')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)
