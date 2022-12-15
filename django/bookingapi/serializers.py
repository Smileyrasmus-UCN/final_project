from .models import Order, Event, Booking, Location, BookableItem
from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    user = serializers.ReadOnlyField(source="created_by.username")
    user_link = serializers.HyperlinkedRelatedField(
        view_name="user-detail", read_only=True, source="created_by"
    )

    def _user(self, obj):
        request = self.context.get("request", None)
        if request:
            return request.user

    class Meta:
        abstract = True


class OrderSerializer(BaseSerializer):
    bookings = serializers.SerializerMethodField()

    def get_bookings(self, obj):
        return obj.bookings.all().values(
            "id",
            "bookable_item__id",
            "bookable_item__name",
            "event__id",
            "event__name",
            "event__start_time",
            "event__end_time",
            "bookable_item__location__name",
        )

    class Meta:
        model = Order
        fields = [
            "url",
            "id",
            "user",
            "created_by",
            "user_link",
            "customer_id",
            "note",
            "bookings",
            "created_at",
            "updated_at",
            "type",
        ]
        read_only_fields = ["bookings"]

    # def validate(self, data):
    #     user = self._user(self)
    #     if user.conditions["order"]["require_customer"]:
    #         if not data["customer_id"]:
    #             raise serializers.ValidationError(
    #                 {"customer_id": "Customer ID is required"}
    #             )
    #     return data


class BookingSerializer(BaseSerializer):
    class Meta:
        model = Booking
        fields = [
            "url",
            "id",
            "created_by",
            "user",
            "user_link",
            "order",
            "event",
            "bookable_item",
            "type",
        ]
        validators = []

    # def validate(self, data):
    #     user = self._user(self)
    #     event = data["event"]
    #     bookable_item = data.get("bookable_item", None)
    #     booking = Booking.objects.filter(created_by=user)
    #     id = self.instance.id if self.instance else None
    #     if id:
    #         booking = booking.exclude(id=id)
    #     if user.conditions["booking"]["require_bookable_item"]:
    #         if not bookable_item:
    #             raise serializers.ValidationError(
    #                 {"bookable_item": "Bookable item is required"}
    #             )
    #     if user.conditions["booking"]["duplicate_booking"] and bookable_item:
    #         if bookable_item:
    #             if booking.filter(event=event, bookable_item=bookable_item).exists():
    #                 raise serializers.ValidationError(
    #                     {"bookable_item": "Booking already exists"}
    #                 )
    #         else:  # if bookable_item is None
    #             if booking.filter(event=event).exists():
    #                 raise serializers.ValidationError(
    #                     {"bookable_item": "Booking already exists"}
    #                 )
    #     return data


class EventSerializer(BaseSerializer):
    class Meta:
        model = Event
        fields = [
            "url",
            "id",
            "created_by",
            "user",
            "user_link",
            "name",
            "description",
            "locations",
            "start_time",
            "end_time",
            "type",
        ]

    # def validate(self, data):
    #     user = self._user(self)
    #     name = data["name"]
    #     start_time = data["start_time"]
    #     end_time = data["end_time"]
    #     id = self.instance.id if self.instance else None
    #     event = Event.objects.all().filter(created_by=user)
    #     if id:
    #         event = event.exclude(id=id)
    #     if user.conditions["event"]["duplicate_event"]:
    #         if event.filter(
    #             name=name, start_time=start_time, end_time=end_time
    #         ).exists():
    #             raise serializers.ValidationError({"name": "Event already exists"})

    #     if user.conditions["event"]["start_end_overlay"]:
    #         if event.filter(
    #             name=name, start_time__lte=start_time, end_time__gte=end_time
    #         ).exists():
    #             raise serializers.ValidationError(
    #                 {"name": "Event overlaps existing event"}
    #             )
    #     return data


class LocationSerializer(BaseSerializer):
    class Meta:
        model = Location
        fields = [
            "url",
            "id",
            "user",
            "created_by",
            "user_link",
            "name",
            "description",
            "events",
            "type",
        ]

    # def validate(self, data):
    #     user = self._user(self)
    #     name = data["name"]
    #     id = self.instance.id if self.instance else None
    #     location = Location.objects.filter(created_by=user)
    #     if id:
    #         location = location.exclude(id=id)
    #     if user.conditions["location"]["duplicate_location"]:
    #         if location.filter(name=name).exists():
    #             raise serializers.ValidationError(
    #                 "Location with this name already exists"
    #             )
    #     return data


class BookableItemSerializer(BaseSerializer):
    class Meta:
        model = BookableItem
        fields = [
            "url",
            "id",
            "user",
            "created_by",
            "user_link",
            "name",
            "description",
            "active",
            "location",
            "type",
        ]

    # def validate(self, data):
    #     user = self._user(self)
    #     name = data["name"]
    #     location = data.get("location", None)
    #     id = self.instance.id if self.instance else None
    #     bookable_item = BookableItem.objects.filter(created_by=user)
    #     if id:
    #         bookable_item = bookable_item.exclude(id=id)
    #     if user.conditions["bookable_item"]["duplicate_bookable_item"]:
    #         if location:
    #             if bookable_item.filter(name=name, location=location).exists():
    #                 raise serializers.ValidationError(
    #                     "Bookable item on this location with this name already exists"
    #                 )
    #         else:
    #             if bookable_item.filter(name=name).exists():
    #                 raise serializers.ValidationError(
    #                     "Bookable item with this name already exists"
    #                 )
    #     return data
