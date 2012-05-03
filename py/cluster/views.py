from django.template import RequestContext
from django.shortcuts import render_to_response
from cluster.models import *
from django.http import HttpResponse, HttpResponseRedirect,HttpResponseNotFound



##class TopMenu():
##    menuitems=['About','Config','Statistic','Documentation']




def index(request):
    all_clusters = HostCluster.objects.all()
    return render_to_response('index.html', {'all_clusters': all_clusters},RequestContext(request))

def not_found(request):
    return HttpResponseNotFound('<h1>Page not found</h1>')


def add_cluster(request):
    cluster=HostCluster()
    if request.method=='POST':
	cluster.set_content_data(request.POST)
	cluster.add_edit()
	return HttpResponseRedirect("/")
    add_form=ClusterForm()
    add_conn_form=ClusterConnParamForm()
    return render_to_response('add_edit_cluster.html',{'add_form':add_form,'add_conn_form':add_conn_form,'message':'Add Cluster Form','action':'add'},RequestContext(request))


def update_cluster(request,cluster_id):
    cluster=HostCluster.objects.get(pk=cluster_id)
    if request.method=='POST':
	cluster.set_content_data(request.POST)
	cluster.add_edit()
	return HttpResponseRedirect("/"+cluster_id)

    add_form={}
    add_form['db_host']=cluster.hostname
    add_form['db_ip_address']=cluster.ip_address
    add_form['db_fqdn']=cluster.fqdn
    add_form['db_is_master']=cluster.is_master
    add_form['db_comments']=cluster.spec_comments
    ae_form=ClusterForm(add_form)

    add_conn_form={}
    add_conn_form['db_name']=cluster.get_conn_param('dbname')
    add_conn_form['db_user']=cluster.get_conn_param('user')
    add_conn_form['db_password']=cluster.get_conn_param('password')
    add_conn_form['db_port']=cluster.get_conn_param('port')
    add_conn_form['db_sslmode']=cluster.get_conn_param('sslmode')
    ae_conn_form=ClusterConnParamForm(add_conn_form)
    return render_to_response('add_edit_cluster.html',{'add_form':ae_form,'add_conn_form':ae_conn_form,'message':'Update Cluster Form','action':'update'},RequestContext(request))

def cluster_queries(request,cluster_id):
    cluster=HostCluster.objects.get(pk=cluster_id)
    queries=cluster.cluster_queries()
    all_clusters = HostCluster.objects.all()
    return render_to_response('cluster_queries.html',{'cluster':cluster,'current_queries':queries,'all_clusters': all_clusters},RequestContext(request))


def cluster_details(request,cluster_id):
    cluster=HostCluster.objects.get(pk=cluster_id)
    dbs=cluster.databasename_set.filter(alive=True).order_by('db_name')
    all_clusters = HostCluster.objects.all()
    return render_to_response('cluster_details.html',{'cluster':cluster,'dbs':dbs,'all_clusters': all_clusters},RequestContext(request))


def discover_cluster(request,cluster_id):
    hc=HostCluster.objects.get(pk=cluster_id)
    hc.discover_cluster()
    return HttpResponseRedirect("/"+cluster_id)


##########################################################################################

def discover_db(request,cluster_id,database_id):
    database=DatabaseName.objects.get(pk=database_id)
    database.discover_database()
    return HttpResponseRedirect("/"+cluster_id+"/"+database_id)

def db_details(request,cluster_id,database_id):
    all_clusters = HostCluster.objects.all()
    cluster=HostCluster.objects.get(pk=cluster_id)
#    hc=HostCluster.objects.get(pk=cluster_id)
    db=DatabaseName.objects.get(pk=database_id)
    sch_set=db.schemaname_set.filter(alive=True).order_by('sch_name')
    return render_to_response('database_details.html',{'cluster':cluster,'database':db,'schemas':sch_set,'all_clusters': all_clusters},RequestContext(request))
#    return HttpResponse("Cluster: "+cluster_id+"<br>Database: "+database_id)

##########################################################################################

def sch_details(request,cluster_id,database_id,schema_id):
    all_clusters = HostCluster.objects.all()
    hc=HostCluster.objects.get(pk=cluster_id)
    db=DatabaseName.objects.get(pk=database_id)
    sch=SchemaName.objects.get(pk=schema_id)
    table_set=sch.tablename_set.filter(alive=True).order_by('tbl_name')
    func_set=sch.functionname_set.filter(alive=True).order_by('func_name')
    return render_to_response('schema_details.html',{'cluster':hc,'database':db,'schema':sch,'tables':table_set,'functions':func_set,'all_clusters': all_clusters},RequestContext(request))

def discover_sch(request,cluster_id,database_id,schema_id):
    hc=HostCluster.objects.get(pk=cluster_id)
    db=DatabaseName.objects.get(pk=database_id)
    sch=SchemaName.objects.get(pk=schema_id)
#    conn=psycopg2.connect(db.get_conn_string())
    sch.discover_schema_tables(db.get_conn_string())
    sch.discover_schema_functions(db.get_conn_string())
    return HttpResponseRedirect("/"+cluster_id+"/"+database_id+"/"+schema_id)

#def about(request):
#    return Ht
