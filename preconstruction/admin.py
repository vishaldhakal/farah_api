from django.contrib import admin
from .models import Developer, PreConstruction, PreConstructionImage, City, PreConstructionFloorPlan, News


class PreConstructionImageAdmin(admin.StackedInline):
    model = PreConstructionImage


class PreConstructionFloorPlanAdmin(admin.StackedInline):
    model = PreConstructionFloorPlan


@admin.register(PreConstruction)
class PreConstructionAdmin(admin.ModelAdmin):
    list_display = ("project_name", "city", "project_type")

    class Meta:
        model = PreConstruction


@admin.register(PreConstructionImage)
class PreConstructionImageAdmin(admin.ModelAdmin):
    pass


@admin.register(PreConstructionFloorPlan)
class PreConstructionFloorPlanAdmin(admin.ModelAdmin):
    pass


admin.site.register(Developer)
admin.site.register(City)
admin.site.register(News)
