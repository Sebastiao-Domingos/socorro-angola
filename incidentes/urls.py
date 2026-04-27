from django.urls import path
from . import views
urlpatterns = [
    path('', views.lista, name='incidentes_lista'),
    path('novo/', views.novo, name='incidentes_novo'),
    path('<int:pk>/', views.detalhe, name='incidentes_detalhe'),
    path('<int:pk>/status/', views.editar_status, name='incidentes_status'),
    path('<int:pk>/alocar/', views.alocar_voluntario, name='incidentes_alocar'),
    path('<int:pk>/remover/<int:vid>/', views.remover_voluntario, name='incidentes_remover'),
    path('<int:pk>/checklist/', views.toggle_checklist, name='incidentes_checklist'),
    path('<int:pk>/relatorio/', views.novo_relatorio, name='incidentes_relatorio'),
]