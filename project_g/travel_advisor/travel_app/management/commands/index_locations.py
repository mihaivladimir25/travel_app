from django.core.management.base import BaseCommand
from travel_app.models import Location
from elasticsearch import Elasticsearch

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        es = Elasticsearch("http://localhost:9200")

        for loc in Location.objects.all():
            es.index(index="locations", id=loc.id, document={
                "name": loc.name,
                "description": loc.description,
                "city": loc.city.name,
                "location_type": loc.location_type
            })

        self.stdout.write(self.style.SUCCESS("Locations indexed successfully"))
