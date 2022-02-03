from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import LoginForm
from .views import home, profile, RegisterView, CustomLoginView, post_create, post_list, post_detail

urlpatterns = [
    path('', home, name='users-home'),
    path('register/', RegisterView.as_view(), name='users-register'),
    path('login/',
         CustomLoginView.as_view(redirect_authenticated_user=True, template_name='users/login.html',
                                 authentication_form=LoginForm), name='login'),
    path('profile/', profile, name='users-profile'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    url(r'^create/$', post_create, name='post_create'),
    url(r'^posts/$', post_list, name='post_list'),
    url(r'^posts/(?P<url>\S+)/$', post_detail, name='post_detail'),

]
