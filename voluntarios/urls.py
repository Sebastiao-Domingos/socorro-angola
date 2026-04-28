from django.urls import path
from . import views
urlpatterns = [
    path('', views.lista, name='voluntarios_lista'),
    path('novo/', views.cadastrar, name='voluntarios_cadastrar'),
    path('registar/', views.registar_publico, name='registar_voluntario'),
    path('<int:pk>/', views.detalhe, name='voluntarios_detalhe'),
    path('<int:pk>/editar/', views.editar, name='voluntarios_editar'),
    path('<int:pk>/disponibilidade/', views.atualizar_disponibilidade, name='voluntarios_disponibilidade'),
]


