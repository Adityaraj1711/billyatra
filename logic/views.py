import logging
from datetime import datetime

from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Business, Customer, Transaction, Role, Staff, Inventory, BillItem, Bill
from .serializers import BusinessSerializer, CustomerSerializer, TransactionSerializer, RoleSerializer, StaffSerializer, \
    InventorySerializer, BillSerializer, BillItemSerializer, UserSerializer, UserBusinessSerializer


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # A user can only access their own business or the business they are staff of
        if hasattr(self.request.user, 'owned_business'):
            return Business.objects.filter(owner=self.request.user)
        elif hasattr(self.request.user, 'staff'):
            return Business.objects.filter(id=self.request.user.staff.business.id)
        return Business.objects.none()

    def perform_create(self, serializer):
        # Automatically set the owner to the logged-in user
        serializer.save(owner=self.request.user)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # A user can only access customers of their associated business
        business = self.request.user.owned_business
        return Customer.objects.filter(business=business)

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # A user can only access inventory of their associated business
        business = self.request.user.owned_business
        return Inventory.objects.filter(business=business)

class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    permission_classes = [IsAuthenticated]

    # http://127.0.0.1:8000/api/bills/?start_date=2023-01-01&end_date=2026-01-31&customer=1&?item_name=paalak
    def get_queryset(self):
        queryset = Bill.objects.filter(
            customer__business=self._get_user_business()
        )

        # Date range filtering
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
                queryset = queryset.filter(created_at__range=[start, end])
            except ValueError:
                pass  # Handle invalid date format if needed

        # Customer filtering
        customer_id = self.request.query_params.get('customer')
        if customer_id:
            queryset = queryset.filter(customer__id=customer_id)

        # BillItem filtering
        item_name = self.request.query_params.get('item_name')
        if item_name:
            queryset = queryset.filter(
                items__inventory_item__name__icontains=item_name
            )

        return queryset.distinct()

    def _get_user_business(self):
        """Helper to get user's business (owner or staff)"""
        if hasattr(self.request.user, 'owned_business'):
            return self.request.user.owned_business
        elif hasattr(self.request.user, 'staff_memberships'):
            return self.request.user.staff_memberships.first().business
        return None

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # A user can only access bills of their associated business
        business = self.request.user.owned_business
        return Transaction.objects.filter(customer__business=business)

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # A user can only access roles of their associated business
        business = self.request.user.owned_business
        return Role.objects.filter(business=business)

class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # A user can only access staff of their associated business
        business = self.request.user.owned_business
        return Staff.objects.filter(business=business)


class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CurrentUserBusinessView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserBusinessSerializer(request.user)
        return Response(serializer.data)
