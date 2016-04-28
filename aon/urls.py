from django.conf.urls import url, include
from django.contrib import admin

from app import views

urlpatterns = [

    # Admin URL
    url(r'^admin/', admin.site.urls),

    # Account,Profile URLs
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url(r'^account/setting/$', views.account_edit, name='edit_account'),
    url(r'^profile/edit/$', views.edit_profile_view, name='edit_profile'),
    url(r'^avatar/', include('avatar.urls')),


    # Project URLs
    url(r'^explore/$', views.explore, name='explore'),
    url(r'^explore/(?P<category_name>[\w-]+)/$', views.filter_projects, name='explore_filter'),
    url(r'^projects/(?P<slug>[\w-]+)/$', views.detail_view, name='project_detail'),
    url(r'^projects/(?P<slug>[\w-]+)/edit', views.edit_view, name='edit_view'),
    url(r'^projects/(?P<slug>[\w-]+)/delete', views.delete_view, name='delete_view'),
    url(r'^search$', views.search, name='search'),

    # Notification
    url(r'^notifications/$', views.notifications, name='notifications'),

    # Offer/Collaborate
    url(r'^offer/accept/$', views.acceptOffer, name='acceptOffer'),
    url(r'^offer/reject/$', views.rejectOffer, name='rejectOffer'),
    url(r'^projects/(?P<slug>[\w-]+)/collaborate/$', views.offer, name='offer'),

    # Profile,Dashboard URL's
    url(r'^users/(?P<user_name>[\w-]+)/$', views.users_profile_view, name='user_profile'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),

    # Static pages
    url(r'^$', views.indexView, name='index'),

    # AJAX
    url(r'^ajax/project/categories/$', views.get_project_categories, name='get_project_categories'),
    url(r'^ajax/project/sub_categories/$', views.get_project_types, name='get_project_types'),
    url(r'^ajax/project/skill_tags/$', views.get_skill_tags, name='get_skill_tags'),
    url(r'^ajax/project/update_progress', views.change_project_status, name='change_project_status'),
    url(r'^ajax/skill_tags/$', views.get_tags, name='get_tags'),
    url(r'^ajax/project/filter/$', views.filter_project, name='filter_project'),
    url(r'^ajax/project/get/$', views.get_project, name='get_project'),
    url(r'^ajax/post/requestoffer/$', views.create_request_offer, name='get_project'),
    url(r'^ajax/project/new/$', views.project_create, name='create_project'),

]
