from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^py/', include('py.foo.urls')),

    url(r'^$', 'cluster.views.index'),
    url(r'^add$', 'cluster.views.add_cluster'),

    url(r'^(?P<cluster_id>\d+)/$', 'cluster.views.cluster_details'),
    url(r'^(?P<cluster_id>\d+)/update/$', 'cluster.views.update_cluster'),
    url(r'^(?P<cluster_id>\d+)/discover/$', 'cluster.views.discover_cluster'),


    url(r'^(?P<cluster_id>\d+)/(?P<database_id>\d+)/$', 'cluster.views.db_details'),
    url(r'^(?P<cluster_id>\d+)/(?P<database_id>\d+)/discover/$', 'cluster.views.discover_db'),

    url(r'^(?P<cluster_id>\d+)/(?P<database_id>\d+)/(?P<schema_id>\d+)/$','cluster.views.sch_details'),



    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
