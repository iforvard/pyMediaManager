"""dev URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.views import serve
from django.http import HttpResponse
from django.urls import path, include, re_path
from django.views.decorators.cache import never_cache


@login_required
def password_404(request):
    return HttpResponse('<h1>Смена пароля и email временно отключена.</h1><br>pyMediaManager')


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'accounts/password/', password_404),
    re_path(r'accounts/email/', password_404),
    path(r'accounts/', include('allauth.urls')),
    path('', include('main.urls', namespace='')),
]

if settings.DEBUG:
    urlpatterns.append(path('static/path:path', never_cache(serve)))
