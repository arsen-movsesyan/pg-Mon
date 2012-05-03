from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('cluster.views',
    # Example:
    # (r'^py/', include('py.foo.urls')),

    url(r'^$', 'index'),
    url(r'^add/$', 'add_cluster'),
    url(r'^about/$', 'not_found'),
    url(r'^doc/$', 'not_found'),

    url(r'^(?P<cluster_id>\d+)/$', 'cluster_details'),
    url(r'^(?P<cluster_id>\d+)/update/$', 'update_cluster'),
    url(r'^(?P<cluster_id>\d+)/queries/$', 'cluster_queries'),
    url(r'^(?P<cluster_id>\d+)/discover/$', 'discover_cluster'),


    url(r'^(?P<cluster_id>\d+)/(?P<database_id>\d+)/$', 'db_details'),
    url(r'^(?P<cluster_id>\d+)/(?P<database_id>\d+)/discover/$', 'discover_db'),

    url(r'^(?P<cluster_id>\d+)/(?P<database_id>\d+)/(?P<schema_id>\d+)/$','sch_details'),
    url(r'^(?P<cluster_id>\d+)/(?P<database_id>\d+)/(?P<schema_id>\d+)/discover/$','discover_sch'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
