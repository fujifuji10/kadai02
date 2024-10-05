from typing import Any
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import (
  View,TemplateView,RedirectView
)
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import (
  CreateView, UpdateView, DeleteView, FormView,
)
from . import forms
from datetime import datetime
from django.contrib import messages
from .models import Housings, HousingPictures
from django.urls import reverse_lazy, reverse
from django.contrib.messages.views import SuccessMessageMixin
from .forms import PictureUploadForm, HouseAddForm, HouseUpdateForm, PictureCreateForm
import logging
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
import os

# application_logger = logging.getLogger('application-logger') #settings.pyのloggersに記載しているので呼び出すと記載の設定で作成してくれる。
# error_logger= logging.getLogger('error-logger')
    
class HomeView(TemplateView):
  template_name = 'account/home.html'

class HouseDetailView(LoginRequiredMixin,DetailView):
  model = Housings
  template_name = os.path.join('house', 'house_detail.html')
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    housing_pictures = HousingPictures.objects.filter(housing=self.object)
    context['housing_pictures'] = housing_pictures
    return context
  
class HousingListView(ListView):
  model = Housings #一覧表示するモデル
  template_name = 'house/list_house.html' #表示するテンプレートの名前
  
  def get_queryset(self):
    query = super().get_queryset()
    name = self.request.GET.get('housing.name', None)
    if name:
      query = query.filter(
        name__icontains = name
      )
    distance = self.request.GET.get('housing.distance', None)
    if distance:
      query = query.filter(
        distance__icontains = distance
      )
    order_by_price = self.request.GET.get('order_by_price', 0)
    if order_by_price == '1':
      query = query.order_by('price')
    elif order_by_price == '2':
      query = query.order_by('-price')
    return query
    
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['housing.name'] = self.request.GET.get('housing.name', '')
    context['housing.distance'] = self.request.GET.get('housing.distance', '')
    order_by_price = self.request.GET.get('order_by_price')
    if order_by_price == '1':
      context['ascending'] = True
    elif order_by_price == '2':
      context['descending'] = True
    return context
  
class HouseCreateView(CreateView):
  model = Housings
  template_name = 'house/house_add.html'
  form_class = HouseAddForm
  success_message = '物件登録が完了しました'
  
  def get_success_url(self):
        return reverse_lazy('house:list_house')
   
  def get_success_message(self, cleaned_data):
        return f'{cleaned_data.get("name")}を登録しました'
  
  def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['picture_form'] = PictureCreateForm()  # PictureCreateFormを追加
        return context
  
class HouseUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'house/house_update.html'
    model = Housings
    form_class = forms.HouseUpdateForm
    success_message = '更新に成功しました'

    def get_success_url(self):
        return reverse('house:list_house')

    def get_success_message(self, cleaned_data):
        return cleaned_data.get('name') + 'を更新しました'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context['picture_form'] = PictureUploadForm() 
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        picture_form = PictureUploadForm(request.POST, request.FILES)
        
        if form.is_valid() and picture_form.is_valid():
            # HouseUpdateFormの情報を保存
            updated_house = form.save(commit=False)
            updated_house.update_at = datetime.now()  # 更新日時を設定
            updated_house.save()

            if 'building_picture' in request.FILES:
              for file in request.FILES.getlist('building_picture'):
                HousingPictures.objects.create(
                  housing=self.object,
                  picture=file,
                  picture_type='building'
              )
            if 'floor_plan' in request.FILES:
              for file in request.FILES.getlist('floor_plan'):
                HousingPictures.objects.create(
                  housing=self.object,
                  picture=file,
                  picture_type='floor'
              )
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
  
class HouseDeleteView(DeleteView):
  model = Housings
  template_name = 'house/house_delete.html'
  success_url = reverse_lazy('house:list_house')
  
def delete_picture(request, pk):
  picture = get_object_or_404(HousingPictures, pk=pk)
  picture.delete()
  import os
  if os.path.isfile(picture.picture.path):
    os.remove(picture.picture.path)
  messages.success(request, '画像を削除しました')
  return redirect('store:edit_book', pk=picture.book.id)