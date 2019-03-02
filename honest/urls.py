from django.urls import path
from . import views

app_name = 'honest'
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('category/<str:category_slug>/', views.category, name='category'),
    path('category/', views.all_categories, name='all_categories'),
    path('add_category/', views.add_category, name='add_category'),
    path('area/<str:area_slug>/', views.area, name='area'),
    path('area/', views.all_areas, name='all_areas'),
    path('add_area/', views.add_area, name='add_area'),
    path('add_person/', views.add_person, name='add_person'),
    #path('register/', views.register, name='register'),
    #path('login/', views.user_login, name='login'),
    #path('logout/', views.logout, name='logout'),
    path('<str:area_slug>/<str:category_slug>/', views.category_in_area, name='category_in_area'),
    path('<str:area_slug>/<str:category_slug>/<int:person_id>', views.person, name='person')
]
