from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ID Card URLs
    path('id-cards/', views.IDCardListView.as_view(), name='id_card_list'),
    path('id-cards/create/', views.IDCardCreateView.as_view(), name='id_card_create'),
    path('id-cards/<int:pk>/', views.IDCardDetailView.as_view(), name='id_card_detail'),
    path('id-cards/<int:pk>/edit/', views.IDCardUpdateView.as_view(), name='id_card_edit'),
    path('id-cards/<int:pk>/print/', views.id_card_print_view, name='id_card_print'),
    path('my-id-card/', views.my_id_card_view, name='my_id_card'),
]