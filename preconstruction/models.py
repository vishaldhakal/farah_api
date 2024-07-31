from django.db import models
from django_summernote.fields import SummernoteTextField
from django.db.models import Case, When, Value, IntegerField

class Developer(models.Model):
    image = models.FileField()
    name = models.CharField(max_length=500)
    slug = models.CharField(max_length=1000, blank=True)
    phone = models.CharField(max_length=200, blank=True)
    website_link = models.TextField(blank=True)
    details = SummernoteTextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class City(models.Model):
    name = models.CharField(max_length=500)
    slug = models.CharField(max_length=1000, unique=True)
    details = SummernoteTextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class PreConstruction(models.Model):

    STATUS_CHOICES = [
        ("Upcoming", "Upcoming"),
        ("Selling", "Selling"),
        ("Archived", "Archived"),
        ("Planning Phase", "Planning Phase"),
        ("Sold out", "Sold out")
    ]

    ASSIGNMENT_CHOICES = [
        ("Free", "Free"),
        ("Not Available", "Not Available"),
        ("Available With Fee", "Available With Fee")
    ]
    PROJECT_CHOICES = [
        ("Condo", "Condo"),
        ("Townhome", "Townhome"),
        ("Semi-Detached", "Semi-Detached"),
        ("Detached", "Detached"),
        ("NaN", "NaN"),
    ]

    developer = models.ForeignKey(Developer, on_delete=models.CASCADE)
    occupancy = models.CharField(max_length=500)
    no_of_units = models.CharField(max_length=500)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=500)
    slug = models.CharField(max_length=1000, unique=True)
    price_starting_from = models.FloatField(default=0)
    price_to = models.FloatField(default=0)
    project_type = models.CharField(
        max_length=500, choices=PROJECT_CHOICES, default="NaN")
    description = SummernoteTextField(blank=True)
    project_address = models.CharField(max_length=500)
    status = models.CharField(
        max_length=500, choices=STATUS_CHOICES, default="Upcoming")
    co_op_available = models.BooleanField(default=False)
    date_of_upload = models.DateField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.project_name

    class Meta:
        ordering = [
            '-last_updated',
            Case(
                When(status="Selling", then=Value(1)),
                When(status="Upcoming", then=Value(2)),
                When(status="Sold out", then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            ),
        ]


class PreConstructionImage(models.Model):
    preconstruction = models.ForeignKey(
        PreConstruction, on_delete=models.CASCADE, related_name='image')
    image = models.FileField()

    def __str__(self):
        if self.image:
            return self.image.url
        else:
            return "/media/no-image.webp"


class PreConstructionFloorPlan(models.Model):
    preconstruction = models.ForeignKey(
        PreConstruction, on_delete=models.CASCADE, related_name='floorplan')
    floorplan = models.FileField()

    def __str__(self):
        return self.floorplan.url




class News(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    news_title = models.CharField(max_length=1000)
    slug = models.CharField(max_length=1000, blank=True)
    news_thumbnail = models.FileField(blank=True)
    news_description = SummernoteTextField(blank=True)
    date_of_upload = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)
    news_link = models.CharField(max_length=2000, default="#")

    def __str__(self):
        return self.event_title
