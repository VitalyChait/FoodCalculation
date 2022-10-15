from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('sign-up', views.sign_up, name='sign_up'),
    path('create_diary', views.create_diary, name='create_diary'),
    path('add_food_note/<int:diary_id>', views.add_food_note, name='add_food_note'),
    path('view_diary/<int:diary_id>', views.view_diary, name='view_diary'),
    path('show_food/<int:food_id>', views.show_photo, name='show_photo'),
    path('update_diary/<int:diary_id>', views.update_diary, name='update_diary'),
    path('search_food.html', views.search_food, name='search_food'),
    path('search_food', views.search_food, name='search_food'),
    path('video_feed', views.video_feed, name='video_feed'),
    path('show_photo', views.show_photo, name='show_photo'),
]
