from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index, name='index'), 
    path('', views.PostList.as_view()),
    
    path('<int:pk>/', views.single_page_post, name='single_page_post'),
]
