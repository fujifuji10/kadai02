from django.db import models
from django.contrib.auth.models import (
  AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from django.db.models.signals import post_save
from django.dispatch import receiver
from uuid import uuid4
from datetime import datetime, timedelta
from django.contrib.auth.models import UserManager
from house.models import BaseModel
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Enter Email')
        user = self.model(
            username=username,
            email=email
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.model(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Users(AbstractBaseUser, PermissionsMixin):
  username = models.CharField(max_length=255) 
  age = models.IntegerField(null=True)
  email = models.EmailField(max_length=255, unique=True)
  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)
  
  objects = UserManager()
  
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['username']
  
  class Meta:
    db_table = 'users'
    
class UserActivateTokensManager(models.Manager):
  
  def activate_user_by_token(self, token): 
    user_activate_token = self.filter(
      token=token,
      expired_at__gte=timezone.now()  # timezone.now() に変更
    ).first()
    
    if user_activate_token:  # トークンが存在するか確認
      user = user_activate_token.user
      user.is_active = True
      user.save()
      return user  # アクティベートしたユーザーを返す
    return None  # 無効なトークンの場合は None を返す
    
class UserActivateTokens(models.Model):
  
  token = models.UUIDField(db_index=True) #検索する際にtokenを起点にしようと思うのでdb_indexを追加した
  expired_at = models.DateTimeField() 
  user = models.ForeignKey(
    'Users', on_delete=models.CASCADE
  )
  
  objects = UserActivateTokensManager()
  
  class Meta:
    db_table = 'user_activate_tokens'
    
@receiver(post_save, sender=Users)
def publish_token(sender, instance, **kwargs): #この引数はセットで使用
  print(str(uuid4)) #uuidでどんな値が出るか確認用
  print(datetime.now() + timedelta(days=1))
  user_activate_token = UserActivateTokens.objects.create(
    user=instance, token=str(uuid4()), expired_at=datetime.now() + timedelta(days=1),
    #user=第二引数のinstance化するという意味のinstanceを指定する
    #user=UserAictiveTokenのuserのこと
    #あとはUserAictiveTokenのtokenとexpired_atを指定する
  )
  print(f'http://127.0.0.1:8000/accounts/activate_user/{user_activate_token.token}')
  # 保存処理後にprintでターミナル上に登録ユーザーのtokenを表示する
  # 本当はメールでURLを送る方が良い。
  
class Comments(models.Model):
  username = models.CharField(max_length=255) 
  comment = models.TextField()
  user = models.ForeignKey(
    'Users', on_delete=models.CASCADE, null=True
  )
  created_at=models.DateTimeField(auto_now_add=True, verbose_name='投稿日時', null=True, blank=False)
  updated_at=models.DateTimeField(auto_now=True, verbose_name='更新日時', null=True, blank=False)
  
  class Meta:
    db_table = 'comments'
    
class Images(models.Model):
  image = models.ImageField(upload_to='images/')
  
  class Meta:
    db_table = 'images'