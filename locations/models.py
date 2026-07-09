from django.db import models
from syncing.mixins import SyncModel

class Location(SyncModel):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    @property
    def table_count(self):
        return self.table_set.count()

class Table(SyncModel):
    STATUS_CHOICES = [
        ('free', 'Bo\'sh'),
        ('busy', 'Band'),
    ]
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='free')
    
    def __str__(self):
        return f"{self.location.name} - {self.name}"
    
    def get_status_color(self):
        return 'orange' if self.status == 'busy' else 'gray'
