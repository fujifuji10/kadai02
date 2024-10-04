from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from . import forms
from django.core.exceptions import ValidationError
from .models import UserActivateTokens
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from datetime import datetime
from django.views.generic.base import (
    View, TemplateView, RedirectView,
)
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import (
  CreateView, UpdateView, DeleteView,FormView,
)
from .forms import RegistForm, UserLoginForm, CommentAddForm
from django.urls import reverse_lazy, reverse
from .models import Users, Comments
from django.contrib.messages.views import SuccessMessageMixin
from house.models import Housings

# Create your views here.
class HomeView(TemplateView):
  template_name = 'account/home.html'

class WelcomeView(TemplateView):
  template_name = 'account/welcome.html'
  
class RegistUserView(CreateView):
  template_name = 'account/regist.html'
  form_class = RegistForm
  success_url = reverse_lazy("account:user_login")
  
class UserLoginView(FormView):
    template_name = 'account/user_login.html'
    form_class = UserLoginForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()  # フォームデータを取得
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)  # 認証処理
            if user is not None and user.is_active:
                login(request, user)  # ユーザーログイン
                return redirect('account:home')  # ログイン成功後にリダイレクト
            else:
                form.add_error(None, "メールアドレスまたはパスワードが正しくありません。")
        return self.form_invalid(form)  # フォームが無効な場合、エラーを表示
  
class UserLogoutView(View):
  
  def get(self, request, *args, **kwargs):
    logout(request)
    return redirect('account:user_login')
  
class UserUpdateView(SuccessMessageMixin, UpdateView):
  template_name = 'account/user_update.html'
  model = Users
  form_class = forms.UserUpdateForm
  success_message = '更新に成功しました'
  
  def get_success_url(self):
    return reverse('account:home')
  
  def get_success_message(self, cleaned_data):
    response_message = cleaned_data.get('name') + "を更新しました" if cleaned_data.get('name') is not None else None
    return response_message
  
  def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        context['id'] = self.kwargs['pk']
        return context
  
class UserCommentListView(ListView):
  model = Comments #一覧表示するモデル
  template_name = 'account/list_comment.html'
  context_object_name = 'user_comment'
  
  def get_queryset(self):
    qs = super(UserCommentListView, self).get_queryset()
    qs = qs.order_by('-id',)
    return qs
  
class CommentAddView(LoginRequiredMixin, CreateView):
  model = Comments
  template_name = 'account/add_comment.html'
  form_class = CommentAddForm
  
  def get_success_url(self):
    return reverse_lazy('account:list_comment', kwargs={"pk": self.object.pk})
  
  def form_valid(self, form):
    form.instance.create_at = datetime.now()
    form.instance.update_at = datetime.now()
    object = form.save(commit=False)
    object.user = self.request.user
    object.save()
    return super(CommentAddView, self).form_valid(form)
  
class CommentUpdateView(SuccessMessageMixin, UpdateView):
  template_name = 'account/update_comment.html'
  model = Comments
  form_class = forms.CommentUpdateForm
  
  def get_success_url(self):
    return reverse_lazy('account:list_comment', kwargs={'pk':self.object.pk})
  
  def get_context_data(self, **kwargs):
        context = super(CommentUpdateView, self).get_context_data(**kwargs)
        context['id'] = self.kwargs['pk']
        return context

class CommentDeleteView(DeleteView):
  model = Comments
  template_name = 'account/delete_comment.html'
  
  def get_success_url(self):
    return reverse_lazy('account:list_comment', kwargs={'pk': self.object.pk})