from django.urls import path
from . import views
from .views import(
  HomeView, RegistUserView, UserLoginView, UserLogoutView, 
  UserUpdateView, WelcomeView, UserCommentListView,CommentAddView, CommentUpdateView, CommentDeleteView
)

app_name = 'account'

urlpatterns = [
  path('home/', HomeView.as_view(), name='home'),
  path('welcome/', WelcomeView.as_view(), name='welcome'),
  path('regist/', RegistUserView.as_view(), name='regist'),
  path('user_login/', UserLoginView.as_view(), name='user_login'),
  path('user_logout/', UserLogoutView.as_view(), name='user_logout'),
  path('user_update/<int:pk>', UserUpdateView.as_view(), name='user_update'),
  path('list_comment/<int:pk>', UserCommentListView.as_view(), name='list_comment'),
  path('add_comment/', CommentAddView.as_view(), name='add_comment'),
  path('update_comment/<int:pk>', CommentUpdateView.as_view(), name='update_comment'),
  path('delete_comment/<int:pk>', CommentDeleteView.as_view(), name='delete_comment'),
]
