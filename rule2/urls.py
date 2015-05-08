from django.conf.urls import include, url, patterns
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    # url(r'', include('rules_app.urls')),
    url(r'^rules/', include('rules_app.urls')),
    )
