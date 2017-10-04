from django.conf.urls import include, url

from budget_sheets import views

urlpatterns = [
url(r'^$',views.index, name='index'),
#url(r'^autocomplete/', include('autocomplete_light.urls')),
url(r'^search/$', views.search, name='search'),
url(r'^search_pdfs/$', views.search_pdfs, name='search_pdfs'),
url(r'^search_pdfs_all/$', views.search_all_pdfs, name='search_all_pdfs'),
url(r'^search_pdfs_all/(?P<id_search>.+)$', views.show_search_all_pdfs, name='show_search_all_pdfs'),
url(r'^update_data/$', views.update_data, name='update_data'),
#url(r'^update_pdfs_data/$', views.update_pdfs_data, name='update_pdfs_data'),
url(r'^list_pdfs/$', views.list_pdfs, name='list_pdfs'),
url(r'^list_finished_pdfs/$', views.finalized, name='finalized'),
url(r'^pdfs/(?P<file_name>.+)$', views.update_pdfs, name='update_pdfs'),
url(r'^list_results/$', views.list_results, name='list_results'),
url(r'^details_charity/(?P<regno_charity>.+)$', views.details_charity, name='details_charity'),
url(r'^autocomplete/', include('autocomplete_light.urls'))
]