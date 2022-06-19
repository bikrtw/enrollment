from django.urls import path

from . import views

urlpatterns = [
    path('nodes/<uuid:node_id>', views.nodes, name='nodes'),
    path('imports', views.imports, name='imports'),
    path('delete/<uuid:node_id>', views.delete, name='delete'),
    path('sales', views.sales, name='sales'),
    path('node/<uuid:node_id>/statistic', views.get_node_statistic,
         name='get_node_statistic'),
]
