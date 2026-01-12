from elasticsearch import Elasticsearch
from django.core.management.base import BaseCommand
from ...models import Location

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        es = Elasticsearch("http://localhost:9200")

        for loc in Location.objects.all():
            es.index(index="locations", id=loc.id, document={
                "name": loc.name,
                "description": loc.description or "",
                "city": loc.city.name if loc.city else "",
                "location_type": loc.location_type or ""
            })

        self.stdout.write(self.style.SUCCESS("Locations indexed."))
