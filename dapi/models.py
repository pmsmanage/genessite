from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Product(models.Model):
    product_name = models.CharField(max_length=200)
    product_description = models.CharField(max_length=20000, blank=True, default="")
    price = models.FloatField(default=1)
    customers = models.ManyToManyField(
        User,
        through='Order',
        through_fields=('product', 'customer')
    )

    def __str__(self):
        return self.product_name


class OrderStatus(models.TextChoices):
    WAITING = 'waiting', _('waiting')
    IN_PRODUCTION = 'in_production', _('in_production')
    READY = 'ready', _('ready')
    DONE = 'done', _('done')


class Order(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.IntegerField()
    total_price = models.FloatField()
    status = models.CharField(max_length=15,
                              choices=OrderStatus.choices,
                              default=OrderStatus.WAITING)
    order_description = models.CharField(max_length=20000, blank=True)

    def __str__(self):
        return str(self.product) + ' ' + str(self.customer)


class DNAService(models.Model):

    class ServiceType(models.TextChoices):
        DNA_SCORING = 'dna_scoring', _('dna_scoring')

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.IntegerField()
    type = models.CharField(max_length=15,
                            choices=ServiceType.choices,
                            default=ServiceType.DNA_SCORING)
    status = models.CharField(max_length=15,
                              choices=OrderStatus.choices,
                              default=OrderStatus.WAITING)
    service_description = models.CharField(max_length=200000, blank=True)

    def total_price(self):
        return self.number*0.09

