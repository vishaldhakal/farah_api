import re
from rest_framework import status
from django.core.mail import EmailMessage
from django.http.response import JsonResponse
from django.shortcuts import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Developer, PreConstruction, PreConstructionImage, City, PreConstructionFloorPlan, News
from .serializers import DeveloperSerializer, PreConstructionSerializer, CitySerializer, PreConstructionImageSerializer, PreConstructionFloorPlanSerializer, NewsSerializer,PreConstructionSerializerSmall, CitySerializerSmall, CitySerializerSmallSearch, PreConstructionSearchSerializer2
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from django.utils.text import slugify
from geopy.geocoders import Nominatim



class DeveloperListCreateView(generics.ListCreateAPIView):
    queryset = Developer.objects.all()
    serializer_class = DeveloperSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        name = data.get('name')
        details = data.get('details')
        website_link = data.get('website_link')
        phone = data.get('phone')
        slug = slugify(name)
        developer = Developer.objects.create(
            name=name, details=details, website_link=website_link, phone=phone, slug=slug)
        serializer = DeveloperSerializer(developer)
        return Response(serializer.data)


class DeveloperRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Developer.objects.all()
    serializer_class = DeveloperSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.data.get('image'):
            instance.image = request.data.get('image')
        instance.name = request.data.get('name')
        instance.details = request.data.get("details")
        instance.website_link = request.data.get('website_link')
        instance.phone = request.data.get('phone')
        if instance.slug != slugify(request.data.get('name')):
            if Developer.objects.filter(slug=slugify(request.data.get('name'))).exists():
                instance.slug = slugify(request.data.get('name')) + "-" + str(instance.id)
            else:
                instance.slug = slugify(request.data.get('name'))
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(['GET'])
def slugify_all_news(request):
    developers = News.objects.all()
    for news in developers:
        news.slug = slugify(news.news_title)
        news.save()
    return Response({"message": "done"})

@api_view(['GET'])
def PreConstructionsDeveloper(request, slug):
    developer = Developer.objects.get(slug=slug)
    dev_serializer = DeveloperSerializer(developer)
    preconstructions = PreConstruction.objects.filter(developer__slug=slug)
    serializer = PreConstructionSerializerSmall(preconstructions, many=True)
    return Response({"developer": dev_serializer.data, "precons": serializer.data})

class CityListCreateView(generics.ListCreateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class CityRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10000


class PreConstructionListCreateView(generics.ListCreateAPIView):
    queryset = PreConstruction.objects.all()
    serializer_class = PreConstructionSerializer
    pagination_class = LargeResultsSetPagination

    def create(self, request, *args, **kwargs):
        data = request.data
        developer_id = data.get('predata[developer][id]')
        city_id = data.get('predata[city][id]')
        developer = Developer.objects.get(id=developer_id)
        city = City.objects.get(id=city_id)
        project_name = data.get('predata[project_name]')

        project_type = data.get('predata[project_type]')
        status = data.get('predata[status]')
        project_address = data.get('predata[project_address]')
        description = data.get('predata[description]')
        co_op = data.get('predata[co_op_available]')
        co_op_available = True if co_op == "true" else False
        price_starting_from = data.get('predata[price_starting_from]')
        price_to = data.get('predata[price_to]')
        occupancy = data.get('predata[occupancy]')
        no_of_units = data.get('predata[no_of_units]')

        """Generate slug from project name with unique in case of same name"""
        slug = slugify(project_name)
        if PreConstruction.objects.filter(slug=slug).exists():
            slug = f'{slug}-{PreConstruction.objects.all().count()}'

        preconstruction = PreConstruction.objects.create(
            developer=developer,
            city=city,
            project_name=project_name,
            slug=slug,
            project_type=project_type,
            status=status,
            project_address=project_address,
            description=description,
            co_op_available=co_op_available,
            price_starting_from=price_starting_from,
            price_to=price_to,
            occupancy=occupancy,
            no_of_units=no_of_units
        )

        """ Save images from images received """
        images = request.data.getlist('images[]')

        for image in images:
            PreConstructionImage.objects.create(
                preconstruction=preconstruction, image=image)

        """ Save floorplans """
        floorplans = request.data.getlist('plans[]')
        for floorplan in floorplans:
            PreConstructionFloorPlan.objects.create(
                preconstruction=preconstruction, floorplan=floorplan)

        preconstruction.save()
        serializer = PreConstructionSerializer(preconstruction)
        return Response(serializer.data)


class PreConstructionRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PreConstruction.objects.all()
    serializer_class = PreConstructionSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        developer_id = data.get('predata[developer][id]')
        city_id = data.get('predata[city][id]')
        developer = Developer.objects.get(id=developer_id)
        city = City.objects.get(id=city_id)
        project_name = data.get('predata[project_name]')
        project_type = data.get('predata[project_type]')
        status = data.get('predata[status]')
        project_address = data.get('predata[project_address]')
        description = data.get('predata[description]')
        co_op = data.get('predata[co_op_available]')
        co_op_available = True if co_op == "true" else False
        price_starting_from = data.get('predata[price_starting_from]')
        price_to = data.get('predata[price_to]')
        occupancy = data.get('predata[occupancy]')
        no_of_units = data.get('predata[no_of_units]')

        instance.developer = developer
        instance.city = city
        instance.project_name = project_name
        instance.project_type = project_type
        instance.status = status
        instance.project_address = project_address
        instance.description = description
        instance.co_op_available = co_op_available
        instance.price_starting_from = price_starting_from
        instance.price_to = price_to
        instance.occupancy = occupancy
        instance.no_of_units = no_of_units

        if instance.slug != slugify(project_name):
            if PreConstruction.objects.filter(slug=slugify(project_name)).exists():
                instance.slug = slugify(project_name) + "-" + str(instance.id)
            else:
                instance.slug = slugify(project_name)

        """ Save images """
        images = request.FILES.getlist('images[]')
        for image in images:
            PreConstructionImage.objects.create(
                preconstruction=instance, image=image)

        """ Save floorplans """
        floorplans = request.FILES.getlist('plans[]')
        for floorplan in floorplans:
            PreConstructionFloorPlan.objects.create(
                preconstruction=instance, floorplan=floorplan)

        instance.save()
        serializer = PreConstructionSerializer(instance)
        return Response(serializer.data)


@api_view(['GET'])
def get_related_precons(request, city):
    precons = PreConstruction.objects.filter(city__slug=city)[:4]
    serializer = PreConstructionSerializerSmall(precons, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def remove_last_part_of_slug(request):
    precons = PreConstruction.objects.all()
    for precon in precons:
        slug = precon.slug.split('-')
        # check if last part is no
        if re.match(r'\d+', slug[-1]):
            new_str = '-'.join(slug[:-1])
            if PreConstruction.objects.filter(slug=new_str).exists():
                new_str = new_str + "-" + str(precon.id)
            precon.slug = new_str
            precon.save()
    return Response({"message": "done"})


@api_view(['GET'])
def PreConstructionDetailView(request, slug):
    preconstruction = PreConstruction.objects.get(slug=slug)
    serializer = PreConstructionSerializer(preconstruction)
    return Response(serializer.data)


@api_view(['GET'])
def PreConstructionsCityView(request, slug):
    status = request.GET.get('status')
    page_size = request.GET.get('page_size',60)
    occupancy = request.GET.get('occupancy')
    project_type = request.GET.get('project_type')
    price_starting_from = request.GET.get('price_starting_from')
    city = City.objects.get(slug=slug)
    cityser = CitySerializer(city)

    preconstructions = PreConstruction.objects.filter(city__slug=slug)
    #add pagination
    paginator = PageNumberPagination()
    paginator.page_size = page_size

    if status:
        preconstructions = preconstructions.filter(status=status)
    if occupancy:
        preconstructions = preconstructions.filter(occupancy=occupancy)
    if project_type:
        preconstructions = preconstructions.filter(project_type=project_type)
    if price_starting_from:
        preconstructions = preconstructions.filter(
            price_starting_from__gte=price_starting_from)

    preconstructions = paginator.paginate_queryset(preconstructions, request)
        
    serializer = PreConstructionSerializerSmall(preconstructions, many=True)
    return Response({"city": cityser.data, "preconstructions": serializer.data})

class NewsListCreateView(generics.ListCreateAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        city_data = data.get('city[name]')
        try:
            city = City.objects.get(name=city_data)
        except City.DoesNotExist:
            return Response({"message": "City not found"}, status=status.HTTP_400_BAD_REQUEST)

        print(data.get('news_thumbnail'))
        news_title = data.get('news_title')
        news_thumbnail = data.get('news_thumbnail')
        news_description = data.get('news_description')
        news_link = data.get('news_link')
        slug = slugify(news_title)

        news = News.objects.create(
            city=city,
            news_title=news_title,
            news_thumbnail=news_thumbnail,
            news_description=news_description,
            news_link=news_link,
            slug=slug
        )
        serializer = NewsSerializer(news)
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        city = request.GET.get('city')
        if city:
            news = News.objects.filter(city__slug=city)
        else:
            news = News.objects.all()
        serializer = NewsSerializer(news, many=True)
        return Response(serializer.data)


class NewsRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        city_data = request.data.get('city[name]')
        try:
            city = City.objects.get(name=city_data)
        except City.DoesNotExist:
            return Response({"message": "City not found"}, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get('news_thumbnail'):
            instance.news_thumbnail = request.data.get('news_thumbnail')
        instance.news_title = request.data.get('news_title')
        instance.news_description = request.data.get('news_description')
        instance.news_link = request.data.get('news_link')
        instance.city = city
        if instance.slug != slugify(request.data.get('news_title')):
            if Developer.objects.filter(slug=slugify(request.data.get('news_title'))).exists():
                instance.slug = slugify(request.data.get('news_title')) + "-" + str(instance.id)
            else:
                instance.slug = slugify(request.data.get('news_title'))
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

@api_view(['GET'])
def news_detail(request, slug):
    news = News.objects.get(slug=slug)
    serializer = NewsSerializer(news)
    return Response(serializer.data)

class CityListCreateView(generics.ListCreateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    """ custom function to create city with only name """

    def create(self, request, *args, **kwargs):
        data = request.data
        city_name = data.get('name')
        city_details = data.get('details')
        base_slug = slugify(city_name)
        unique_slug = base_slug
        num = 1
        while City.objects.filter(slug=unique_slug).exists():
            unique_slug = base_slug + "-" + str(num)
            num += 1
        city = City.objects.create(
            name=city_name, slug=unique_slug, details=city_details)
        serializer = CitySerializer(city)
        return Response(serializer.data)


class CityRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.name = request.data.get('name')
        city_details = request.data.get('details')
        base_slug = slugify(request.data.get('name'))
        unique_slug = base_slug
        instance.slug = unique_slug
        instance.details = city_details
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)



@api_view(['DELETE'])
def delete_image(request, pk):
    image = PreConstructionImage.objects.get(id=pk)
    image.delete()
    return JsonResponse("Deleted Successfully", safe=False)


@api_view(['DELETE'])
def delete_floorplan(request, pk):
    floorplan = PreConstructionFloorPlan.objects.get(id=pk)
    floorplan.delete()
    return JsonResponse("Deleted Successfully", safe=False)


@api_view(['GET'])
def get_all_city(request):
    cities = City.objects.all()
    serializer = CitySerializerSmall(cities, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_all_precons(request):
    cities = City.objects.all()
    serializer = CitySerializerSmallSearch(cities, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_all_precons_city(request,slug):
    cities = City.objects.get(slug=slug)
    serializer = CitySerializerSmallSearch(cities)
    return Response(serializer.data)

@api_view(['GET'])
def get_all_precons_search(request):
    precons = PreConstruction.objects.all()
    serializer = PreConstructionSearchSerializer2(precons, many=True)

    cities = City.objects.all()
    serializer2 = CitySerializerSmall(cities,many=True)

    return Response({"projects": serializer.data, "cities": serializer2.data})


def validate_name(name):
    """
    Validates the name field.
    Returns True if name is valid, False otherwise.
    """
    if not name:
        return False
    # Add additional name validation logic here if needed
    return True


def validate_email(email):
    """
    Validates the email field.
    Returns True if email is valid, False otherwise.
    """
    if not email:
        return False
    if '@' not in email:
        return False
    # Add additional email validation logic here if needed
    return True


def validate_phone(phone):
    """
    Validates the phone field.
    Returns True if phone is valid, False otherwise.
    """
    if not phone:
        return False
    # Add additional phone validation logic here if needed
    return True


def validate_message(message):
    """
    Validates the message field.
    Returns True if message is valid, False otherwise.
    """
    if not message:
        return False
    # Add additional message validation logic here if needed
    return True

@api_view(["POST"])
def ContactFormSubmission(request):
    if request.method == "POST":
        subject = "Inquiry about " + \
            request.POST["proj_name"]+" in " + \
            request.POST["cityy"]+" - Dolphy"
        emaill = "Dolphy <info@dolphy.ca>"
        headers = {'Reply-To': request.POST["email"]}

        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        message = request.POST["message"]
        realtor = request.POST["realtor"]

        if validate_name(request.POST["name"]) and validate_email(request.POST["email"]) and validate_phone(request.POST["phone"]):
            body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}\nIs a realtor?: {realtor}"
            email = EmailMessage(
                subject, body, emaill, ["hello@dolphy.ca"],
                reply_to=[email], headers=headers
            )
            email.send(fail_silently=False)
            return HttpResponse("Sucess")
        else:
            email = EmailMessage(
                subject, body, emaill, ["hello@dolphy.ca"],
                reply_to=[email], headers=headers
            )
            email.send(fail_silently=False)
            return HttpResponse("Sucess")
    else:
        return HttpResponse("Not post req")
    


def getlatlong(request):
    add = request.GET.get("address")
    loc = Nominatim(user_agent="Geopy Library")

    # entering the location name
    getLoc = loc.geocode(add)

    # printing latitude and longitude
    return JsonResponse({'lat':getLoc.latitude,'long':getLoc.longitude})