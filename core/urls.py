"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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

# core/urls.py

from django.contrib import admin
from django.urls import path, include
from matchmaking.views import MatchCreateView, MatchUpdateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),  # accounts 앱의 url 연결
    path('matches/create/', MatchCreateView.as_view(), name='create-match'),  # 매치 생성
    path('matches/update/<int:match_id>/', MatchUpdateView.as_view(), name='update-match'),  # 매치 수정
]
