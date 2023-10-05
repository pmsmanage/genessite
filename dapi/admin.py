from django.contrib import admin
from .models import Product, Order, DNAService
# Register your models here.

admin.site.register(Order)
admin.site.register(Product)
admin.site.register(DNAService)
