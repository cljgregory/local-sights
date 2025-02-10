from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from .api import api
from localsights.maps import views

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="pages/home.html"),
        name="home",
    ),
    path(
        "about/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),


    path("locations/", views.LocationListView.as_view(), name="locations"),
    path("locations/<int:pk>/", views.LocationDetailView.as_view(), name="location-detail"),
    path('locations/create/', views.LocationCreateView.as_view(), name='location-create'),
    path('location/<int:pk>/update/', views.LocationUpdateView.as_view(), name='location-update'),
    path('location/<int:pk>/delete/', views.LocationDeleteView.as_view(), name='location-delete'),

    path("maps/", views.MapListView.as_view(), name="maps"),
    path("maps/<int:pk>/", views.MapDetailView.as_view(), name="map-detail"),
    path('maps/create/', views.MapCreateView.as_view(), name='map-create'),
    path('map/<int:pk>/update/', views.MapUpdateView.as_view(), name='map-update'),
    path('map/<int:pk>/delete/', views.MapDeleteView.as_view(), name='map-delete'),

    path(
        "geocoding/<int:pk>/",
        views.GeocodingView.as_view(),
        name="geocoding"
    ),
    path(
        "distance/",
        views.DistanceView.as_view(),
        name="distance"
     ),
    path(
        "display_map/",
        views.DisplayMapView.as_view(),
        name="display_map"
     ),

    #  path('', include('maps.urls')),


    # path("maps/create/", views.createMap, name="create",
    # ),
    
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path(
        "users/",
        include("localsights.users.urls", namespace="users"),
    ),
    path("accounts/", include("allauth.urls")),
    path("api/", api.urls),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls))
        ] + urlpatterns