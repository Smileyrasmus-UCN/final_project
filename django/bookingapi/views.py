from .serializers import *
from .models import *
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwner
from rest_framework.response import Response
from django.db import transaction
from rest_framework.decorators import action
from django.db.transaction import get_connection
from django.shortcuts import render
from .models import Constraints
from .forms import ConstraintsForm


class BaseReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset.all()
        return self.queryset.filter(created_by=self.request.user)

    class Meta:
        abstract = True


class BaseViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset.all()
        return self.queryset.filter(created_by=self.request.user)

    class Meta:
        abstract = True


class LocationViewSet(BaseViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_fields = ["name"]


class BookableItemViewSet(BaseViewSet):
    queryset = BookableItem.objects.all()
    serializer_class = BookableItemSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_fields = ["name", "location"]

    def create(self, request, *args, **kwargs):
        """
        #checks if post request data is an array initializes serializer with many=True
        else executes default CreateModelMixin.create function
        """
        is_many = isinstance(request.data, list)
        if not is_many:
            return super(BookableItemViewSet, self).create(request, *args, **kwargs)
        else:
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )


class EventViewSet(BaseViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_fields = ["name", "start_time", "end_time"]


class BookingViewSet(BaseReadOnlyViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_fields = ["event"]

    @action(detail=False, url_path="bookable-items")
    def get_bookable_items_only(self, request):
        if not request.query_params.get("event"):
            return Response(
                {"event": "This field is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        bookable_items = self.filter_queryset(self.queryset).values("bookable_item")
        # make to a list of strings instead of list of objects
        bookable_items_ids = map(lambda b: b["bookable_item"], bookable_items)
        return Response(bookable_items_ids)


class OrderViewSet(BaseViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_fields = ["customer_id"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["created_at"]

    def get_queryset(self):
        event_id = self.request.query_params.get("event_id")
        if event_id:
            return (
                self.filter_queryset(self.queryset)
                .filter(bookings__event__id__exact=event_id)
                .distinct()
            )
        return super().get_queryset()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        if not request.data.get("bookings"):
            return Response(
                {"bookings": "This field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # The only way to block a potential double booking, is to lock the whole database table.
        # It is not enough to just lock all of the rows of the table, because this action creates
        # new rows, which also needs to be locked, until transaction is either committed og rolled back.
        cursor = get_connection().cursor()
        cursor.execute(f"LOCK TABLE bookingapi_booking")

        order_serializer = self.get_serializer(data=request.data["order"])
        headers = None
        try:
            order_serializer.is_valid(raise_exception=True)
            self.perform_create(order_serializer)
            order_headers = self.get_success_headers(order_serializer.data)

            # create bookings with order id
            id = order_serializer.data["id"]
            bookings = request.data["bookings"]
            for booking in bookings:
                booking["order"] = id

            self.serializer_class = BookingSerializer
            booking_serializer = self.get_serializer(data=bookings, many=True)
            booking_serializer.is_valid(raise_exception=True)
            self.perform_create(booking_serializer)
            booking_headers = self.get_success_headers(booking_serializer.data)

            # merge 2 dicts
            headers = order_headers.update(booking_headers)
        finally:
            # close the cursor and thereby unlock the table
            cursor.close()

        return Response(
            order_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    # @transaction.atomic
    # def create(self, request, *args, **kwargs):
    #     if not request.data.get("bookings"):
    #         return Response(
    #             {"bookings": "This field is required."},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )
    #     serializer = self.get_serializer(data=request.data["order"])
    #     serializer.is_valid(raise_exception=True)
    #     instance = serializer.save()
    #     for booking in request.data["bookings"]:
    #         booking["order"] = instance.id
    #         self.serializer_class = BookingSerializer
    #         booking_serializer = self.get_serializer(data=booking)
    #         booking_serializer.is_valid(raise_exception=True)
    #         booking_serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)


def constraints_view(request):
    # Check if the form has been submitted
    if request.method == "POST":
        # Check if the user wants to create a new constraint or edit an existing one
        if "constraint_name" in request.POST:
            # The user wants to edit an existing constraint
            # Retrieve the Constraints object with the specified ID
            constraint = Constraints.objects.get(name=request.POST["name"])
        else:
            if Constraints.objects.filter(name=request.POST["name"]).exists():
                return request.POST["name"] + " already exists"
            # The user wants to create a new constraint
            # Create a new Constraints object
            constraint = Constraints()

        # Bind the form data to the form instance
        form = ConstraintsForm(request.POST, instance=constraint)

        # Check if the form data is valid
        if form.is_valid():
            # Save the form data to the Constraints model
            form.save()

    # Retrieve all Constraints objects
    constraints = Constraints.objects.all()

    # Create an instance of the ConstraintsForm
    form = ConstraintsForm()

    # Render the template with the form instance and the list of Constraints objects
    return render(
        request, "constraints.html", {"form": form, "constraints": constraints}
    )
