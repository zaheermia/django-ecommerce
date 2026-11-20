"""Serializers for the API (they turn the models into JSON or XML)."""
from rest_framework import serializers

from .models import Store, Product, Review


class StoreSerializer(serializers.ModelSerializer):
    # the vendor is whoever is logged in so it can't be sent in the request
    """Turn a Store into JSON or XML."""

    vendor = serializers.ReadOnlyField(source='vendor.id')
    vendor_username = serializers.ReadOnlyField(source='vendor.username')

    class Meta:
        """Set the model and fields for the serializer."""

        model = Store
        fields = ['id', 'vendor', 'vendor_username', 'name', 'description']


class ProductSerializer(serializers.ModelSerializer):
    # the store comes from the URL so it can't be sent in the request
    """Turn a Product into JSON or XML."""

    store = serializers.ReadOnlyField(source='store.id')

    class Meta:
        """Set the model and fields for the serializer."""

        model = Product
        fields = ['id', 'store', 'name', 'description', 'price', 'stock']

    def validate_price(self, value):
        """Make sure the price is not negative."""
        if value < 0:
            raise serializers.ValidationError("Price can't be negative.")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """Turn a Review into JSON or XML."""

    product_name = serializers.ReadOnlyField(source='product.name')
    buyer = serializers.ReadOnlyField(source='buyer.username')

    class Meta:
        """Set the model and fields for the serializer."""

        model = Review
        fields = [
            'id', 'product', 'product_name', 'buyer',
            'rating', 'comment', 'verified', 'date',
        ]
