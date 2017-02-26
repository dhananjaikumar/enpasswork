from django.core.management.base import NoArgsCommand
import datetime
from django.utils.timezone import utc
from otp.models import Otp

class Command(NoArgsCommand):
    help="Mark exipred otp"
    def handle_noargs(self, **options):
        objs=Otp.objects.all()
        for a in objs:
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            timediff = now - a.created_at
            '''
            expire after 30 min
            '''
            if timediff.total_seconds()>1800:
                a.expired=True
                a.save()
            
