from rest_framework import serializers
from django.contrib.auth.models import User, Group
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import Product, Order, DNAService

import json


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    group = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'first_name', 'last_name', 'group']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "password fields didn't match"})
        try:
            Group.objects.get(name=attrs['group'])
        except:
            raise serializers.ValidationError({"group": "invalid group"})
        user = self.context['request'].user
        if not user.is_superuser:
            if attrs['group'] != 'customer':
                raise serializers.ValidationError({"user": "user not allow to create this type of users"})
            elif not (user.groups.filter(name='orgs').exists()):  # user must be an org to create customers
                raise serializers.ValidationError({"user": "user not allow to create this type of users"})
        return attrs

    def create(self, validated_data):
        if validated_data['group'] == 'staff':
            user = User.objects.create_superuser(
                username=validated_data['username'],
                email=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name']
            )
        else:
            user = User.objects.create(
                username=validated_data['username'],
                email=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name']
            )

        user.set_password(validated_data['password'])
        user.save()
        Group.objects.get(name=validated_data['group']).user_set.add(user)
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    @staticmethod
    def validate_email(value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    @staticmethod
    def validate_username(value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already in use.")
        return value

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if not user.is_superuser:
            if user.pk != instance.pk:
                raise serializers.ValidationError({"authorize": "you don't have permissions to do this"})

        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.email = validated_data['email']
        instance.username = validated_data['username']

        instance.save()

        return instance


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "password fields didn't match."})

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.is_superuser:
            if not user.check_password(value):
                raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if not user.is_superuser:
            if user.pk != instance.pk:
                raise serializers.ValidationError({"authorize": "you don't have permissions to do this"})

        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class ActivateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    active = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('password', 'active')

    @staticmethod
    def validate_active(value):
        if value in ['True', 'False']:
            return value
        raise serializers.ValidationError({"active": "active should be True or False"})

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if not user.is_superuser:
            if user.pk != instance.pk:
                raise serializers.ValidationError({"authorize": "you don't have permissions to do this"})
            if not user.is_active:
                raise serializers.ValidationError({"user": "you can't Activate your account ask a staff to do that"})
            if not instance.check_password(validated_data['password']):
                raise serializers.ValidationError({"password": "wrong password"})

        a_user = User.objects.get(pk=instance.pk)
        a_user.is_active = validated_data['active']
        a_user.save()

        return instance


class CreateUpdateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_name', 'product_description', 'price']
        extra_kwargs = {
            'product_name': {'required': True},
            'price': {'required': True}
        }

    def create(self, validated_data):
        user = self.context['request'].user

        if not user.is_superuser:
            raise serializers.ValidationError({"user": "you don't have permissions to do this"})

        product = Product.objects.create(
            product_name=validated_data['product_name'],
            price=validated_data['price'])
        try:
            product.product_description = validated_data['product_description']
        except:
            product.product_description = ''
        product.save()
        return product

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if not user.is_superuser:
            raise serializers.ValidationError({"user": "you don't have permissions to do this"})

        instance.price = validated_data['price']
        instance.product_name = validated_data['product_name']

        try:
            instance.product_description = validated_data['product_description']
        except:
            instance.product_description = ''
        instance.save()
        return instance


class CreateOrderSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(required=True)
    customer_id = serializers.IntegerField(required=True)

    class Meta:
        model = Order
        fields = ['product_id', 'customer_id', 'number', 'order_description', 'status', 'total_price']
        extra_kwargs = {
            'number': {'required': True},
            'total_price': {'required': False}
        }

    @staticmethod
    def validate_product_id(value):
        try:
            Product.objects.get(pk=value)
        except:
            raise serializers.ValidationError({"product": "invalid product id"})
        return value

    def create(self, validated_data):
        user = self.context['request'].user

        if not user.is_superuser:
            order = Order.objects.create(
                product=Product.objects.get(pk=validated_data['product_id']),
                customer=user,
                number=validated_data['number'],
                status='waiting',
                total_price=Product.objects.get(pk=validated_data['product_id']).price * validated_data['number']
            )
        else:
            try:
                user = User.objects.get(pk=validated_data['customer_id'])
            except:
                raise serializers.ValidationError({"user": "super users must provide valid customer"})

            order = Order()
            order.customer = user
            order.product = Product.objects.get(pk=validated_data['product_id'])
            order.number = validated_data['number']
            try:
                order.total_price = validated_data['total_price']
            except:
                order.total_price = Product.objects.get(pk=validated_data['product_id']).price * validated_data[
                    'number']

            try:
                status = validated_data['status']
                order.status = status
            except:
                pass
        try:
            order.order_description = validated_data['order_description']
        except:
            order.order_description = ''
        order.save()

        return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(required=False)
    customer_id = serializers.IntegerField(required=False)

    class Meta:
        model = Order
        fields = ['product_id', 'customer_id', 'number', 'order_description', 'status', 'total_price']
        extra_kwargs = {
            'number': {'required': False},
            'total_price': {'required': False}
        }

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if not user.is_superuser:
            raise serializers.ValidationError({"user": "you don't have permissions to do this"})

        try:
            instance.total_price = validated_data['total_price']
        except:
            pass

        try:
            instance.customer = User.objects.get(pk=validated_data['customer_id'])
        except:
            pass

        try:
            instance.product = Product.objects.get(pk=validated_data['product_id'])
        except:
            pass

        try:
            instance.number = validated_data['number']
        except:
            pass

        try:
            instance.order_description = validated_data['order_description']
        except:
            pass

        instance.save()
        return instance


class CreateDNAScoringServiceSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(required=False)

    class Meta:
        model = DNAService
        fields = ['customer_id', 'service_description', 'number', 'status', 'type']
        extra_kwargs = {
            'number': {'required': False},
            'type': {'required': False},
            'status': {'required': False},
            'service_description': {'required': True}
        }

    @staticmethod
    def gene_scoring(gene):
        if len(gene) < 10 or len(gene) > 5000:  # 10 instead of 300 for testing
            return False
        if not all(ch in "ATGC" for ch in gene):
            return False
        ratio = (gene.count('G') + gene.count('C')) * 1.0 / len(gene)
        if ratio <= 0.25 or ratio >= 0.65:
            return False
        return True

    @staticmethod
    def dna_scoring(dna):
        is_valid = True
        if len(dna) > len(set(dna)):
            is_valid = False
        results = []
        valid_count = 0
        number_of_proteins = 0
        for gene in dna:
            number_of_proteins += len(gene)
            if CreateDNAScoringServiceSerializer.gene_scoring(gene):
                results.append("valid")
                valid_count += 1
            else:
                results.append("invalid")
        if len(dna) > valid_count:
            is_valid = False

        return is_valid, results, number_of_proteins

    def create(self, validated_data):
        user = self.context['request'].user

        is_valid, results, number_of_proteins = self.dna_scoring(json.loads(validated_data['service_description']))

        if not is_valid:
            raise serializers.ValidationError({"status": "invalid DNA", "results": results})

        if user.is_superuser:
            try:
                user = User.objects.get(pk=validated_data['customer_id'])
            except:
                raise serializers.ValidationError({"user": "super users have to provide valid customer_id"})
        service = DNAService()
        service.ServiceType = 'dna_scoring'
        service.customer = user
        service.number = number_of_proteins
        service.service_description = validated_data['service_description']
        service.save()
        return service


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'groups', 'first_name', 'last_name']
