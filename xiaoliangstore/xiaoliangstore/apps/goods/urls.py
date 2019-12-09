from django.urls import path
from . import views
rlpatterns = [
    path(r'^categories/(?P<category_id>\d+)/skus/$', views.SKUListView.as_view()),
]
router = DefaultRouter()
router.register('skus/search', views.SKUSearchViewSet, base_name='skus_search')