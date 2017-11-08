from django.core.management.base import BaseCommand

from account.utils import send_bulk_reminders


class Command(BaseCommand):
    help = 'Send reminders to users who have not signed in today'

    def handle(self, *args, **options):
        self.stdout.write('Preparing to send reminder emails...')
        send_bulk_reminders()
        self.stdout.write('Successfully sent reminders')
