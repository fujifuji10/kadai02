from django.db import models
from django.urls import reverse_lazy
from django.dispatch import receiver
import os
import logging

application_logger = logging.getLogger('application-logger')

class BaseModel(models.Model):
  create_at = models.DateTimeField()
  update_at = models.DateTimeField()
  
  class Meta:
    abstract = True #abstractクラスとして抽象的なモデルを作成※実際のモデルは下に定義
    
class Housings(BaseModel):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    zip_code = models.CharField(max_length=7, null=True)  # CharFieldに変更し、郵便番号の形式に対応
    address = models.CharField(max_length=100, null=True)
    distance = models.CharField(max_length=30, null=True)
    floor = models.CharField(max_length=10, null=True)
    house_kind = models.CharField(max_length=20, null=True)
    construction = models.IntegerField(null=True)  # "constraction"を"construction"に修正
    floor_number = models.IntegerField(null=True)
    
    # 新しい画像フィールドを追加
    building_picture = models.ForeignKey(
        'HousingPictures', related_name='building_pictures', on_delete=models.CASCADE, blank=True, null=True
    )
    floor_plan = models.ForeignKey(
        'HousingPictures', related_name='floor_plans', on_delete=models.CASCADE, blank=True, null=True
    )
    
    class Meta:
        db_table = 'housing'

    def __str__(self):
      return self.name

class HousingPicturesManager(models.Manager):
    def filter_by_housing(self, housing):
        return self.filter(housing=housing).all()

class HousingPictures(models.Model):  # BaseModelではなく、Djangoの標準的なモデル
    PICTURE_TYPES = [
        ('building', '物件写真'),
        ('floor', '間取り図'),
    ]
    
    picture = models.FileField(upload_to='housing_pictures/')
    housing = models.ForeignKey('Housings', on_delete=models.CASCADE, null=True)  # null=True を追加して、既存レコードにNULLを許可
    picture_type = models.CharField(max_length=10, choices=PICTURE_TYPES, default='building')
    order = models.IntegerField(blank=True, null=True)
    objects = HousingPicturesManager()
    
    class Meta:
        db_table = 'housing_pictures'
        ordering = ['order']
    
    def __str__(self):
        if self.housing:
            return self.housing.name + ': ' + str(self.order)
        else:
            return 'No House Assigned: ' + str(self.order)
  
# 複数画像フィールドに対応するため、delete_pictureの修正
@receiver(models.signals.post_delete, sender=HousingPictures)
def delete_picture(sender, instance, **kwargs):
    if instance.picture and os.path.isfile(instance.picture.path):
        try:
            os.remove(instance.picture.path)
            application_logger.info(f'{instance.picture.path} を削除しました')
        except Exception as e:
            application_logger.error(f'ファイル削除エラー: {e}')