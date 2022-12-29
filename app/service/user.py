from django.contrib.auth.models import User

from app.models import UserPayment


def create_default_payment_for_users():
    users = User.objects.all()
    for user in users:
        try:
            user = user.payment_info
        except Exception as e:
            print(e)
            payment = UserPayment.objects.create(user=user)
            payment.save()
