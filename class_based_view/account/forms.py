from django import forms
from .models import Users,Comments
from django.contrib.auth.password_validation import validate_password
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.auth import authenticate, login
import re

class RegistForm(forms.ModelForm):
  error_css_class = 'text-danger'
  username = forms.CharField(label='ユーザー名')
  age = forms.IntegerField(label='年齢', min_value=0)
  email = forms.EmailField(label='メールアドレス')
  password = forms.CharField(label='パスワード',validators=[MinLengthValidator(8)],widget=forms.PasswordInput)
  confirm_password = forms.CharField(label='パスワード再入力', validators=[MinLengthValidator(8)],widget=forms.PasswordInput)

  class Meta:
      model = Users
      fields = ['username', 'age', 'email', 'password']

  def clean(self):
      cleaned_data = super().clean()  # 継承元のcleanメソッドを呼び出し、全てのフィールドデータを取得
      password = cleaned_data.get("password")
      confirm_password = cleaned_data.get("confirm_password")
      
      def clean_username(self):
        username = self.cleaned_data.get('username')

    # Noneまたは空文字列を確認
        if not username:
            raise ValidationError('ユーザー名を入力してください')
        
        if re.search(r'\s', username):
            raise ValidationError('ユーザー名にスペースキーを使用しないでください')

    # メールアドレスのような形式をチェック
        if '@' in username:
            raise ValidationError('ユーザー名にメールアドレスを使用しないでください')

        return username
    
        # パスワードとパスワード再入力が一致しているかチェック
      if password and confirm_password and password != confirm_password:
          raise ValidationError("パスワードとパスワード再入力が一致しません。")

      return cleaned_data
  
class UserLoginForm(forms.Form):
  error_css_class = 'text-danger'
  email = forms.CharField(label='メールアドレス')
  password = forms.CharField(label='パスワード', widget=forms.PasswordInput)
  
  def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(username=email, password=password)
        if user is None:
            raise forms.ValidationError("正しいメールアドレスとパスワードを入力してください。")
        return self.cleaned_data
  
class UserUpdateForm(forms.ModelForm):
    error_css_class = 'text-danger'
    username = forms.CharField(label='名前')
    age = forms.IntegerField(label='年齢', min_value=0)
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(
        label='パスワード',
        validators=[
            MinLengthValidator(8),
            RegexValidator(
                regex=r'^[0-9a-zA-Z@¥*:;!$%&]+$',
                message='パスワードには数字、アルファベット、記号（＠￥＊：；！＄％＆）のみ使用できます'
            )
        ],
        widget=forms.PasswordInput
    )
    confirm_password = forms.CharField(
        label='パスワード再入力',
        validators=[
            MinLengthValidator(8),
            RegexValidator(
                regex=r'^[0-9a-zA-Z@¥*:;!$%&]+$',
                message='パスワードには数字、アルファベット、記号（＠￥＊：；！＄％＆）のみ使用できます'
            )
        ],
        widget=forms.PasswordInput
    )

    class Meta:
        model = Users
        fields = ['username', 'age', 'email', 'password']
        
    def clean_username(self):
        username = self.cleaned_data.get('username')

    # Noneまたは空文字列を確認
        if not username:
            raise ValidationError('ユーザー名を入力してください')

    # スペースが含まれているか確認
        if re.search(r'\s', username):
            raise ValidationError('ユーザー名にスペースキーを使用しないでください')

    # メールアドレスのような形式をチェック
        if '@' in username:
            raise ValidationError('ユーザー名にメールアドレスを使用しないでください')

        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # パスワードとパスワード再入力が一致しているかチェック
        if password and confirm_password and password != confirm_password:
            # フィールドエラーを追加しないようにし、非フィールドエラーのみ追加
            self.add_error(None, "パスワードとパスワード再入力が一致しません。")

        return cleaned_data
  
class CommentAddForm(forms.ModelForm):
  error_css_class = 'text-danger'
  # name = forms.CharField(label='ユーザー名')
  # comment = forms.CharField(label='物件への口コミ')
  # created_at = forms.IntegerField(label='投稿日')
    
  class Meta:
    model = Comments
    fields = ('username', 'comment')
    
  def save(self, *args, **kwargs):
    obj = super(CommentAddForm, self).save(commit=False) #classのobjがobjに入る。
    obj.create_at = datetime.now() #このdatetime(現在時刻)は標準ライブラリを使用（datetimeをインポート要)
    obj.update_at = datetime.now()
    obj.save()
    return obj
  
class CommentUpdateForm(forms.ModelForm):
  error_css_class = 'text-danger'
  comment = forms.CharField(label='コメント', widget=forms.Textarea(attrs={'cols':'30', 'rows':'10'}), required=False)
  
  class Meta:
    model = Comments
    fields = ('comment',) #パスワードは別の画面で更新する動きにする