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

    def get_queryset(self):
        # A user can only access bills of their associated business
        business = self.request.user.owned_business
        return Bill.objects.filter(customer__business=business)

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
