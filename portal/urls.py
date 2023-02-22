from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import include
from rest_framework.routers import SimpleRouter
from store.views import ProductViewSet, auth, UserRelationView
from django.conf import settings


router = SimpleRouter()

router.register(r'product', ProductViewSet)
router.register(r'product_relation', UserRelationView)

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('', include('social_django.urls', namespace='social')),
    path('auth/', auth),
]

urlpatterns += router.urls

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns