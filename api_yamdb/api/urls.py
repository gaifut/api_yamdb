from django.urls import include, path

from v1.urls import router_v1

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
