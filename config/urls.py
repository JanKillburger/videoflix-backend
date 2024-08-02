"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include,path, re_path
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from videoflix.views import SignUpView, activate_user, request_password_reset, reset_password, get_media, login, check_email, Videos, VideoCategories, VideoViewSet

router = DefaultRouter()
router.register(r'videos', VideoViewSet, basename='video')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/categories/', VideoCategories.as_view()),
    path('api/login/', login),
    path('admin/', admin.site.urls),
    path('django-rq/', include('django_rq.urls')),
    path('api/signup/', SignUpView.as_view(), name='signup'),
    path('api/activate/', activate_user, name='activate-user'),
    path('__debug__', include('debug_toolbar.urls')),
    path('api/check-email/',check_email),
    path('api/request-password-reset/', request_password_reset),
    path('api/reset-password/<str:reset_token>/', reset_password),
]

urlpatterns += [re_path(r'^media/(?P<path>.*)', get_media)]
