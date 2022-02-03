from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index, name='index'), 
    # path('<int:pk>/', views.single_page_post, name='single_page_post'),
    
    path('', views.PostList.as_view()),    
    path('<int:pk>/', views.PostDetail.as_view()),
    path('category/<str:slug>/', views.category_page),
    path('tag/<str:slug>/', views.tag_page),
    path('create_post/', views.PostCreate.as_view()),
    
]