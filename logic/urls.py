from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessViewSet, CustomerViewSet, TransactionViewSet, RoleViewSet, StaffViewSet, InventoryViewSet, BillViewSet, UserRegistrationView, CurrentUserBusinessView

router = DefaultRouter()
router.register(r'businesses', BusinessViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'inventories', InventoryViewSet)
router.register(r'bills', BillViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'staff', StaffViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('current-user/', CurrentUserBusinessView.as_view(), name='current-user-business'),
]
