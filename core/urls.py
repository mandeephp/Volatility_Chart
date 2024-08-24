from django.urls import path

from core.views import chart_view, home

urlpatterns = [
    path('', home, name='home'),
    path('chart/', chart_view, name='chart'),
    # path('chart/', get_chart_data, name='get_chart_data'),
]