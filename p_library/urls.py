from p_library import views
from p_library.views import CreateUserProfile, AuthorEdit, AuthorList, author_create_many, \
    books_authors_create_many, FriendEdit, FriendUpdate, FriendDelete, PLibraryLoginView, PLibrarySignupView, \
    PLibraryLogoutView
from django.urls import path


app_name = 'p_library'
urlpatterns = [
    path('', views.index),
    path('links/', views.links, name='links'),
    path('accounts/login/', PLibraryLoginView.as_view(), name='login',),
    path('accounts/signup/', PLibrarySignupView.as_view(), name='signup'),
    path('accounts/logout/', PLibraryLogoutView.as_view(), name='logout'),
    path('profile-create/', CreateUserProfile.as_view(), name='profile-create'),
    path('books_list_index/', views.books_list_index),
    path('index/book_increment/', views.book_increment),
    path('index/book_decrement/', views.book_decrement),
    path('publishers/', views.publishers),
    path('author/create/', AuthorEdit.as_view(), name='author_create'),
    path('authors/', AuthorList.as_view(), name='author_list'),
    path('author/create_many/', author_create_many, name='author_create_many'),
    path('author_book/create_many/', books_authors_create_many, name='author_book_create_many'),
    path('friends/', views.friends, name='friends_list'),
    path('friends/create/', FriendEdit.as_view(), name='friend_create'),
    path('friends/friend_edith/<int:pk>/', FriendUpdate.as_view(), name='friend_edith'),
    path('friends/friend_edith/<int:pk>/delete/', FriendDelete.as_view(), name='friend_delete'),
]