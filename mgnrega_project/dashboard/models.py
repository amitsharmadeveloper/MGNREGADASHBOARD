from django.db import models

class DistrictPerformance(models.Model):
    state_name = models.CharField(max_length=100)
    district_name = models.CharField(max_length=100)
    year = models.IntegerField()
    month = models.CharField(max_length=20)
    total_households = models.IntegerField()
    total_persondays = models.IntegerField()
    women_participation = models.FloatField()
    total_expenditure = models.FloatField()
    wages_paid = models.FloatField()

    def __str__(self):
        return f"{self.district_name} ({self.month} {self.year})"
