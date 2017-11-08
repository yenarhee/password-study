from django.core.management.base import BaseCommand

from account.utils import send_reminder_email


class Command(BaseCommand):
    help = 'Send reminders to user with specified email'

    def add_arguments(self, parser):
        parser.add_argument('email', nargs='*', type=str)

    def handle(self, *args, **options):
        emails = options['email']
        for email in emails:
            self.stdout.write('Preparing to send reminder email to %s' % email)
            send_reminder_email(email)
        self.stdout.write('Successfully sent reminder')
