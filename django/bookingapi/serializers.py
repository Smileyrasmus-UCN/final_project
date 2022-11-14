from django.contrib.auth.models import User, Group
from rest_framework import serializers

from bookingapi.models import *


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class BookableLocationSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = BookableLocation
        fields = ["url", "id", "name", "description", "user"]
        read_only_fields = ["user"]


class SeatSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source="created_by.username")
    bookable_location_link = serializers.HyperlinkedRelatedField(view_name="bookablelocation-detail", read_only=True)

    class Meta:
        model = Seat
        fields = [
            "url",
            "id",
            "name",
            "description",
            "restricted",
            "bookable_location",
            "user",
            "bookable_location_link",
        ]
        read_only_fields = ["user"]


class LocationBookingSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source="created_by.username")
    bookable_location_link = serializers.HyperlinkedRelatedField(view_name="bookablelocation-detail", read_only=True)
    
    class Meta:
        model = LocationBooking
        fields = [
            "url",
            "id",
            "bookable_location",
            "start_time",
            "end_time",
            "event_name",
            "event_description",
            "user",
            "bookable_location_link",
        ]
        read_only_fields = ["user"]


class SeatBookingSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source="created_by.username")
    seat_link = serializers.HyperlinkedRelatedField(view_name="seat-detail", read_only=True)
    location_booking_link = serializers.HyperlinkedRelatedField(view_name="locationbooking-detail", read_only=True)

    class Meta:
        model = SeatBooking
        fields = ["url", "id", "customer", "seat", "location_booking", "user", "seat_link", "location_booking_link"]
        read_only_fields = ["user"]
