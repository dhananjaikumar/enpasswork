import time

from threading import Thread
from django.core.mail import EmailMultiAlternatives,get_connection
from django.template.loader import get_template
from django.conf import settings





class EmailThread(Thread):
    def __init__(self, subject, template_path, recipient_list, extra_context=None):
        self.subject = subject
        self.recipient_list = recipient_list
        self.template = get_template(template_path)
        self.extra_context = extra_context or {}
        Thread.__init__(self)

    def run(self):
        connection = get_connection()
        connection.open()
        for user in self.recipient_list:
            self.extra_context['username'] = user.email if not user.membername else user.membername
            self.extra_context['email'] = user.email
            self.extra_context['organization'] = user.organization
            self.extra_context['organization_id'] = user.organization.organizationId

            temp_context = self.extra_context
            html_content = self.template.render(temp_context)
            msg = EmailMultiAlternatives(self.subject, html_content, settings.SERVER_EMAIL, [user.email])
            msg.attach_alternative(html_content, "text/html")
            if 'obj' in self.extra_context.keys():
                order=self.extra_context['obj']
                msg.attach('invoice_%s.pdf'%self.extra_context['order_id'], order.invoice.read(), 'application/pdf')
                self.extra_context.pop('obj',None)
            msg.send()
            time.sleep(1)
        connection.close()