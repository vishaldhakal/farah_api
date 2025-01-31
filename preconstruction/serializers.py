from rest_framework import serializers
from .models import Developer, City, PreConstruction, PreConstructionImage, PreConstructionFloorPlan, News


class DeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Developer
        fields = '__all__'
        ordering = ['name']

class DeveloperSerializerSmall(serializers.ModelSerializer):
    class Meta:
        model = Developer
        fields = ['id','name']
        ordering = ['name']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'
        ordering = ['name']


class CitySerializerSmall(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'slug']

class CitySerializerSmallestt(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['slug']

class CitySerializerSmallSearch(serializers.ModelSerializer):
    preconstructions = serializers.SerializerMethodField()
    class Meta:
        model = City
        fields = ['id', 'name', 'slug','preconstructions']

    def get_preconstructions(self, obj):
        preconstructions = PreConstruction.objects.filter(city=obj)
        serializer = PreConstructionSearchSerializer(preconstructions, many=True)
        return serializer.data


class PreConstructionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreConstructionImage
        fields = ('id', 'image')
        ordering = ['id']


class PreConstructionFloorPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreConstructionFloorPlan
        fields = ('id', 'floorplan')
        ordering = ['id']


class PreConstructionSerializer(serializers.ModelSerializer):
    image = PreConstructionImageSerializer(many=True, read_only=True)
    floorplan = PreConstructionFloorPlanSerializer(many=True, read_only=True)
    city = CitySerializer()
    developer = DeveloperSerializer()

    class Meta:
        model = PreConstruction
        fields = '__all__'
        ordering = ['last_updated']

class PreConstructionSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreConstruction
        fields = ['id','slug','project_name']
        ordering = ['last_updated']

class PreConstructionSearchSerializer2(serializers.ModelSerializer):
    city = CitySerializerSmallestt()
    class Meta:
        model = PreConstruction
        fields = ['id','slug','project_name','city']
        ordering = ['last_updated']


class PreConstructionSerializerSmall(serializers.ModelSerializer):
    image = PreConstructionImageSerializer(many=True, read_only=True)
    city = CitySerializerSmall()
    developer = DeveloperSerializerSmall()

    class Meta:
        model = PreConstruction
        fields = '__all__'
        ordering = ['last_updated']


class NewsSerializer(serializers.ModelSerializer):
    city = CitySerializer()

    class Meta:
        model = News
        fields = '__all__'
        ordering = ['date_of_upload']