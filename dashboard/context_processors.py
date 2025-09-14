from django.db import models
from django.db.models.functions import TruncDay
from django.db.models import Count
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timezone import now, timedelta

def custom_admin_context(request):
    from accounts.models import CustomUser, SelfieWithTree
    from donation.models import ManualPayment, Donation, Registration_fee

    context = {}
    if request.path.startswith('/admin/') and 'login' not in request.path:
        pending_manual_payments = ManualPayment.objects.filter(status='PENDING').count() or 0
        total_users = CustomUser.objects.count()
        total_donations = round(Donation.objects.aggregate(total=models.Sum('amount'))['total'] or 0, 2)
        unverified_series = SelfieWithTree.objects.filter(status='pending').count() or 0
        total_registration_fees = round(Registration_fee.objects.aggregate(total=models.Sum('amount'))['total'] or 0, 2)

        # Chart data (x = date, y = number of users)
        thirty_days_ago = now() - timedelta(days=60)
        chart_data = CustomUser.objects.filter(date_joined__gte=thirty_days_ago) \
            .annotate(date=TruncDay("date_joined")) \
            .values("date") \
            .annotate(y=Count("id")) \
            .order_by("-date")


        chart_data2 = CustomUser.objects.all() \
            .annotate(date=TruncDay("date_joined")) \
            .values("date") \
            .annotate(y=Count("id")) \
            .order_by("-date")


        # print(chart_data2)
        context = {
            "total_users": total_users,
            "total_donations": total_donations,
            "pending_manual_payments": pending_manual_payments,
            "unverified_series": unverified_series,
            "total_registration_fees": total_registration_fees,
            "chart_data": json.dumps(list(chart_data), cls=DjangoJSONEncoder),
        }
    return context
