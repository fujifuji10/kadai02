from django.urls import path
from .views import HomeView, HouseDetailView, HousingListView, HouseCreateView, HouseUpdateView, HouseDeleteView, delete_picture
from django.views.generic.base import TemplateView
from django.views.generic.base import RedirectView
from . import views

app_name = 'house'

urlpatterns = [
  path('house_detail/<int:pk>', HouseDetailView.as_view(), name='house_detail'),
  path('list_house/', views.HousingListView.as_view(), name='list_house'),
  path('house_add/', HouseCreateView.as_view(), name='house_add'),
  path('house_update/<int:pk>', HouseUpdateView.as_view(), name='house_update'),
  path('house_delete/<int:pk>', HouseDeleteView.as_view(), name='house_delete'),
  path('google/', RedirectView.as_view(url='http://google.co.jp')),
  path('delete_picture/<int:pk>', delete_picture, name='delete_picture'),
]