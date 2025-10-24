from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset/done/', views.password_reset_done, name='password_reset_done'),

    path('borrower/', views.borrower_dashboard, name='borrower'),
    path('admin_books/', views.admin_books, name='admin_books'),
    path('add_book/', views.add_book, name='add_book'),
    path('remove_book/<int:book_id>/', views.remove_book, name='remove_book'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:record_id>/', views.return_book, name='return_book'),

    path('search/', views.search_books, name='search_books'),
    path('review/<int:book_id>/', views.add_review, name='add_review'),
]