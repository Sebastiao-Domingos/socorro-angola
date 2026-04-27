from django.urls import path
from . import views
urlpatterns = [
    path('', views.lista, name='doacoes_lista'),
    path('nova/', views.nova_central, name='doacoes_nova'),
    path('<int:pk>/', views.detalhe, name='doacoes_detalhe'),
    path('<int:pk>/doar/', views.registar_doacao, name='doacoes_registar'),
    path('<int:pk>/editar/', views.editar_central, name='doacoes_editar'),
]