from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	 (r'^', include('dst.urls')),
    # Examples:
    # url(r'^$', 'dsp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
urlpatterns += patterns('', url(r'^silk', include('silk.urls', namespace='silk')))
