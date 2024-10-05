from django import forms #絶対必要
from .models import Housings, HousingPictures #booksにデータをそうにゅうするため
from datetime import datetime #現在時刻を表記するため
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator
import re
from django.core.exceptions import ValidationError
from django.utils import timezone

class HouseAddForm(forms.ModelForm):
    error_css_class = 'text-danger'
    name = forms.CharField(label='物件名')
    zip_code = forms.CharField(
        label='郵便番号',
        validators=[RegexValidator(
            regex=r'^[0-9０-９]{7}$',  # 7桁の半角・全角数字のみ許可
            message='7桁の数字のみ入力してください。',
        )],
        widget=forms.TextInput(attrs={'placeholder': '例: 1234567'})
    )
    address = forms.CharField(label='住所')
    distance = forms.CharField(label='最寄駅からの距離')
    price = forms.IntegerField(
        label='家賃', 
        min_value=10000, 
        widget=forms.NumberInput(attrs={'step': '1000'})  # 1000単位で増減
    )
    FLOOR_CHOICES = [
        ('1R', '1R'),
        ('1K', '1K'),
        ('1DK', '1DK'),
        ('1LDK', '1LDK'),
        ('2DK', '2DK'),
        ('2LDK', '2LDK'),
        ('3DK', '3DK'),
        ('3LDK', '3LDK'),
    ]
    floor = forms.ChoiceField(
        label='間取り', 
        choices=FLOOR_CHOICES
    )
    house_kind = forms.CharField(label='物件の種類', initial='賃貸')
    construction = forms.IntegerField(label='築年数', min_value=1)
    floor_number = forms.IntegerField(label='階数', min_value=1)
    building_picture = forms.FileField(label='物件写真', required=False)
    floor_plan = forms.FileField(label='間取り図', required=False)

    class Meta:
        model = Housings
        fields = ['name', 'zip_code', 'address', 'distance', 'price', 'floor', 'house_kind', 'construction', 'floor_number', 'building_picture', 'floor_plan']
    
    # nameフィールドのバリデーション
    def clean_name(self):
      name = self.cleaned_data.get('name')
      if not name:
        raise ValidationError('物件名は必須です。')
      if ' ' in name:
        raise ValidationError('物件名にスペースを含めることはできません。')
      if '@' in name:
        raise ValidationError('物件名に「@」を含めることはできません。')
      return name

    # 全体のバリデーション
    def clean(self):
      cleaned_data = super().clean()
      price = cleaned_data.get('price')
      distance = cleaned_data.get('distance')
      
      if price is not None and price < 1000:
        if not distance:
          raise ValidationError('家賃が安すぎます。適正な価格を記載ください。または最寄駅からの距離を入力する必要があります。')
        
        # 物件名と住所の組み合わせがユニークかどうかのチェック
      name = cleaned_data.get('name')
      address = cleaned_data.get('address')
      if not self.instance.pk:  # 新規作成時のみチェック
        if Housings.objects.filter(name=name, address=address).exists():
          raise ValidationError('同じ物件名と住所の組み合わせが既に存在しています。')
    
    def save(self, *args, **kwargs):
      obj = super(HouseAddForm, self).save(commit=False)
      obj.create_at = timezone.now()
      obj.update_at = timezone.now()
      obj.save()

      if self.cleaned_data['building_picture']:
        building_picture = HousingPictures.objects.create(
        picture=self.cleaned_data['building_picture'],  # ここでファイルを保存
        housing=obj,  # 関連付けるHousingsインスタンス
        picture_type='building',  # picture_typeを指定
        order=1
        )
        print(f"Building picture saved: {building_picture}")
        obj.building_picture = building_picture  # ForeignKeyにセット

      if self.cleaned_data['floor_plan']:
        floor_plan = HousingPictures.objects.create(
        picture=self.cleaned_data['floor_plan'],
        housing=obj,
        picture_type='floor',  # picture_typeを指定
        order=2
        )
        print(f"Floor plan saved: {floor_plan}") 
        obj.floor_plan = floor_plan

      obj.save()
      return obj

class HouseUpdateForm(forms.ModelForm):
    error_css_class = 'text-danger'
    name = forms.CharField(label='物件名')
    zip_code = forms.CharField(
        label='郵便番号',
        validators=[RegexValidator(
            regex=r'^[0-9０-９]{7}$',  # 7桁の半角・全角数字のみ許可
            message='7桁の数字のみ入力してください。',
        )],
        widget=forms.TextInput(attrs={'placeholder': '例: 1234567'})
    )
    address = forms.CharField(label='住所')
    distance = forms.CharField(label='最寄駅からの距離')
    price = forms.IntegerField(
        label='家賃', 
        min_value=10000, 
        widget=forms.NumberInput(attrs={'step': '1000'})  # 1000単位で増減
    )
    FLOOR_CHOICES = [
        ('1R', '1R'),
        ('1K', '1K'),
        ('1DK', '1DK'),
        ('1LDK', '1LDK'),
        ('2DK', '2DK'),
        ('2LDK', '2LDK'),
        ('3DK', '3DK'),
        ('3LDK', '3LDK'),
    ]
    floor = forms.ChoiceField(
        label='間取り', 
        choices=FLOOR_CHOICES
    )
    house_kind = forms.CharField(label='物件の種類', initial='賃貸')
    construction = forms.IntegerField(label='築年数', min_value=1)
    floor_number = forms.IntegerField(label='階数', min_value=1)
    building_picture = forms.FileField(label='物件写真', required=False)
    floor_plan = forms.FileField(label='間取り図', required=False)

    class Meta:
        model = Housings
        fields = ['name', 'zip_code', 'address', 'distance', 'price', 'floor', 'house_kind', 'construction', 'floor_number', 'building_picture', 'floor_plan']
      
        # nameフィールドのバリデーション
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError('物件名は必須です。')
        elif '  ' in name:
          raise ValidationError('物件名にスペースキーを使用しないでください')
        elif ' ' in name:
          raise ValidationError('物件名にスペースキーを使用しないでください')
        return name

    # 全体のバリデーション
    def clean(self):
        cleaned_data = super().clean()

        price = cleaned_data.get('price')
        distance = cleaned_data.get('distance')
        
        if price is not None and price < 1000:
            if not distance:
                raise ValidationError('家賃が安すぎます。適正な価格を記載ください。または最寄駅からの距離を入力する必要があります。')

        # 物件名と住所の組み合わせがユニークかどうかのチェック
        name = cleaned_data.get('name')
        address = cleaned_data.get('address')
        if not self.instance.pk:  # 新規作成時のみチェック
            if Housings.objects.filter(name=name, address=address).exists():
                raise ValidationError('同じ物件名と住所の組み合わせが既に存在しています。')

        return cleaned_data
      
    def save(self, *args, **kwargs):
        obj = super(HouseUpdateForm, self).save(commit=False)
        obj.update_at = timezone.now()
        obj.save()
        return obj
  
class PictureUploadForm(forms.ModelForm):
  error_css_class = 'text-danger'
  building_picture = forms.FileField(required=False)
  floor_plan = forms.FileField(required=False)
  
  class Meta:
    model = HousingPictures
    fields = ['building_picture','floor_plan']
  
  def save(self, house=None, *args, **kwargs):
        obj = super(PictureUploadForm, self).save(commit=False)
        obj.create_at = timezone.now()
        obj.update_at = timezone.now()
        
        if house:
            obj.house = house
        
        if self.cleaned_data.get('building_picture'):
          obj.save()  # HousingPictures モデルを保存
        elif self.cleaned_data.get('floor_plan'):
          obj.save()  # HousingPictures モデルを保存
        return obj
      
class PictureCreateForm(forms.ModelForm):
  error_css_class = 'text-danger'
  building_picture = forms.FileField(required=False)
  floor_plan = forms.FileField(required=False)
  
  class Meta:
    model = HousingPictures
    fields = ['building_picture','floor_plan']
  
  def save(self, house=None, *args, **kwargs):
        obj = super(PictureCreateForm, self).save(commit=False)
        obj.create_at = timezone.now()
        obj.update_at = timezone.now()
        
        if house:
            obj.house = house
        
        if self.cleaned_data.get('building_picture'):
          obj.save()  # HousingPictures モデルを保存
        elif self.cleaned_data.get('floor_plan'):
          obj.save()  # HousingPictures モデルを保存
        return obj