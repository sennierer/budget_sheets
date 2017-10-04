from django.conf.urls import include, url

from django.contrib import admin
from budget_sheets import views

from autocomplete_light import shortcuts as al

al.autodiscover()

admin.autodiscover()

admin.site.site_header = 'Bath charity administration'

urlpatterns = [
    # Examples:
    # url(r'^$', 'bath.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^budget_sheets/', include('budget_sheets.urls')),
	url(r'^$',views.index, name='index'),
    url(r'^login/$', views.user_login, name='user_login')
]
