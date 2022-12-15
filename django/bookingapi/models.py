from django.conf import settings
from django.db import models
import uuid
from django.db.models import UniqueConstraint, Q, CheckConstraint, F


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)s_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)s_updated_by",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class Constraints(models.Model):
    name = models.CharField(max_length=255, unique=True, primary_key=True)
    # Order
    require_customer_on_order = models.BooleanField(default=True)
    # Booking
    duplicate_booking = models.BooleanField(default=True)
    require_bookable_item_on_booking = models.BooleanField(default=False)
    # Event
    duplicate_event = models.BooleanField(default=True)
    start_end_overlay = models.BooleanField(default=True)
    # Location
    duplicate_location = models.BooleanField(default=True)
    # Bookable Item
    duplicate_booking = models.BooleanField(default=True)

    def get_fields(self):
        # Get all field names in the model
        field_names = [field.name for field in self._meta.fields]

        # Remove the "name" field from the list of fields
        field_names.remove("name")

        # Return the list of fields
        return field_names


class Order(BaseModel):
    customer_id = models.CharField(max_length=255, null=True, blank=True)
    note = models.CharField(max_length=255, blank=True, null=True)

    type = models.ForeignKey(
        Constraints,
        on_delete=models.CASCADE,
        related_name="order_constraints",
        # Default is id of default constraint
        default="default",
    )

    class Meta:
        constraints = []
        if Q(type__require_customer_on_order=True):
            constraints.append(
                CheckConstraint(check=Q(customer_id__isnull=False), name="customer_id")
            )


class Event(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    type = models.ForeignKey(
        Constraints,
        on_delete=models.CASCADE,
        related_name="event_constraints",
        default="default",
    )

    class Meta:
        constraints = []
        if Q(type__duplicate_event=True):
            constraints.append(
                UniqueConstraint(
                    fields=["created_by", "start_time", "end_time"], name="unique_event"
                )
            )
        if Q(type__start_end_overlay=True):
            constraints.append(
                CheckConstraint(
                    check=Q(start_time__lt=F("end_time")), name="start_lt_end"
                )
            )


class Location(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    events = models.ManyToManyField("Event", related_name="locations", blank=True)

    type = models.ForeignKey(
        Constraints,
        on_delete=models.CASCADE,
        related_name="location_constraints",
        default="default",
    )

    class Meta:
        constraints = []
        if Q(type__duplicate_location=True):
            constraints.append(
                UniqueConstraint(fields=["name", "created_by"], name="unique_location")
            )


class BookableItem(BaseModel):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="seats", null=True, blank=True
    )
    type = models.ForeignKey(
        Constraints,
        on_delete=models.CASCADE,
        related_name="bookable_item_constraints",
        default="default",
    )

    class Meta:
        constraints = []
        if Q(type__duplicate_bookable_item=True):
            constraints.append(
                UniqueConstraint(
                    fields=["name", "location", "created_by"],
                    name="unique_bookable_item",
                )
            )


class Booking(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="bookings")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="bookings")
    bookable_item = models.ForeignKey(
        BookableItem,
        on_delete=models.CASCADE,
        related_name="bookings",
        null=True,
        blank=True,
    )
    type = models.ForeignKey(
        Constraints,
        on_delete=models.CASCADE,
        related_name="booking_constraints",
        default="default",
    )

    class Meta:
        constraints = []
        if Q(type__duplicate_booking=True):
            constraints.append(
                UniqueConstraint(
                    fields=["order", "event", "bookable_item"],
                    name="unique_booking",
                )
            )
        if Q(type__require_bookable_item_on_booking=True):
            constraints.append(
                CheckConstraint(
                    check=Q(bookable_item__isnull=False), name="bookable_item"
                )
            )
