from rest_framework import serializers
from .models import Business, Customer, Transaction, Role, Staff, Inventory, BillItem, Bill, User

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'

    def validate_owner(self, value):
        # Ensure a user can only own one business
        if Business.objects.filter(owner=value).exists():
            raise serializers.ValidationError("A user can only own one business.")
        return value

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'


class BillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillItem
        fields = ['inventory_item', 'quantity', 'price']


class BillSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True)

    class Meta:
        model = Bill
        fields = ['id', 'customer', 'total_amount', 'payment_mode', 'created_at', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')  # Extract items data
        bill = Bill.objects.create(**validated_data)  # Create the Bill object

        for item_data in items_data:
            inventory_item = item_data['inventory_item']
            quantity = item_data['quantity']

            # Check if the requested quantity is available in the inventory, can uncomment later
            # if inventory_item.current_stock < quantity:
            #     raise serializers.ValidationError(f"Not enough stock for {inventory_item.name}")

            # Deduct the quantity from the inventory
            inventory_item.current_stock -= quantity
            inventory_item.save()

            BillItem.objects.create(bill=bill, **item_data)

        return bill

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items')  # Extract items data

        # Update the Bill object
        instance.customer = validated_data.get('customer', instance.customer)
        instance.total_amount = validated_data.get('total_amount', instance.total_amount)
        instance.payment_mode = validated_data.get('payment_mode', instance.payment_mode)
        instance.save()

        # Delete existing BillItem objects for this bill
        instance.items.all().delete()

        # Create new BillItem objects for each item in the payload
        for item_data in items_data:
            BillItem.objects.create(bill=instance, **item_data)

        return instance

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

