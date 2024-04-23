from django.core.management.base import BaseCommand
from core.models import JobOffer, Responsibility, Requirement, Availability, Category, Mode


class Command(BaseCommand):
    help = 'Borra todos los datos de la base de datos'

    def handle(self, *args, **kwargs):
        self.stdout.write('Borrando todos los datos de la base de datos...')
        Responsibility.objects.all().delete()
        Requirement.objects.all().delete()
        Availability.objects.all().delete()
        JobOffer.objects.all().delete()
        Category.objects.all().delete()
        Mode.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Data successfully deleted'))