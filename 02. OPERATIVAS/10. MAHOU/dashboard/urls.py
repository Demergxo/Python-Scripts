from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("produccion/", views.produccion, name="produccion"),
    path("inbound/", views.inbound, name="inbound"),
    path("outbound/", views.outbound, name="outbound"),

]
