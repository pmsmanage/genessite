from .models import Order


def check_ready_and_send_email():
    try:
        orders = Order.objects.filter(status='ready')
        for order in orders:
            email = order.customer.email
            print(email)
            order.status = 'done'
            order.save()
    except:
        pass
