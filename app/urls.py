from django.urls import path

from . import views

app_name = 'app'

urlpatterns = [
    # Flat pages
    path('', views.home, name='home'),
    path('profile', views.profile, name='profile'),
    path('statistic', views.statistic, name='statistic'),
    path('statistic/api', views.statistic_api, name='statistic_api'),
    path('configuration', views.configuration, name='configuration'),

    # Staffs
    path('staff/curator', views.curator_list, name='curator_list'),
    path('staff/support', views.support_list, name='support_list'),
    path('staff/accountant', views.accountant_list, name='accountant_list'),
    path('staff/admin', views.admin_list, name='admin_list'),
    path('staff/create', views.user_create, name='user_create'),
    path('staff/<int:pk>', views.user_detail, name='user_detail'),
    path('staff/<int:pk>/update', views.user_update, name='user_update'),
    path('staff/<int:pk>/delete', views.user_delete, name='user_delete'),

    # Curator
    path('staff/curator/<str:username>', views.curator_detail, name='curator_detail'),
    path('staff/curator/<str:username>/update', views.curator_update, name='curator_update'),
    path('staff/curator/<str:username>/statistic', views.curator_preview_statistic, name='curator_preview_statistic'),
    path('staff/curator/<str:username>/payment', views.curator_preview_payments, name='curator_preview_payments'),
    path('staff/curator/<str:username>/payment/<int:period_id>', views.curator_preview_payment_detail,
         name='curator_preview_payment_detail'),
    path('staff/curator/<str:username>/executors/internship', views.curator_preview_internship_executor_list,
         name='curator_preview_internship_executor_list'),
    path('staff/curator/<str:username>/executors', views.curator_preview_executor_list,
         name='curator_preview_executor_list'),
    path('staff/curator/<str:username>/free', views.curator_preview_executor_free_list,
         name='curator_preview_executor_free_list'),
    path('staff/curator/<str:username>/add/<int:pk>', views.executor_add_for_curator_by_admin,
         name='executor_add_for_curator_by_admin'),

    path('profile/payment', views.curator_payments, name='curator_payments'),
    path('profile/payment/<int:period_id>', views.curator_payment_detail,
         name='curator_payment_detail'),

    # Executor Internship Files
    path('executor/internship/file', views.executor_internships_file_list, name='executor_internships_file_list'),
    path('executor/internship/file/create', views.executor_internships_file_create,
         name='executor_internships_file_create'),
    path('executor/internship/file/<int:pk>/parse', views.executor_internships_file_parse,
         name='executor_internships_file_parse'),

    # Executor phone Files
    path('executor/phones/file', views.executor_phones_file_list, name='executor_phones_file_list'),
    path('executor/phones/file/create', views.executor_phones_file_create, name='executor_phones_file_create'),
    path('executor/phones/file/<int:pk>/parse', views.executor_phones_file_parse, name='executor_phones_file_parse'),

    # Executor hours Files
    path('executor/hours/file', views.executor_hours_file_list, name='executor_hours_file_list'),
    path('executor/hours/file/<int:pk>/preview', views.executor_hours_file_preview, name='executor_hours_file_preview'),
    path('executor/hours/file/create', views.executor_hours_file_create, name='executor_hours_file_create'),
    path('executor/hours/file/<int:pk>/parse', views.executor_hours_file_parse, name='executor_hours_file_parse'),
    path('executor/hours/file/<int:pk>/delete', views.executor_hours_file_delete, name='executor_hours_file_delete'),

    # Executor list Files
    path('executor/file', views.executor_file_list, name='executor_file_list'),
    path('executor/file/create', views.executor_file_create, name='executor_file_create'),
    path('executor/file/<int:pk>/parse', views.executor_file_parse, name='executor_file_parse'),

    # Executors
    path('executor', views.executor_list, name='executor_list'),
    path('executor/create', views.executor_create, name='executor_create'),
    path('executor/search', views.executor_search, name='executor_search'),
    path('executor/my', views.executor_list_my, name='executor_list_my'),
    path('executor/free', views.executor_list_free, name='executor_list_free'),
    path('executor/debtors', views.executor_list_debtor, name='executor_list_debtor'),
    path('executor/<int:pk>/add', views.executor_add_for_curator, name='executor_add_for_curator'),
    path('executor/<int:pk>/add/api', views.executor_add_for_curator_by_api, name='executor_add_for_curator_by_api'),
    path('executor/<path:executor_id>/update', views.executor_update, name='executor_update'),
    path('executor/<int:pk>/delete', views.executor_delete, name='executor_delete'),
    path('executor/<path:executor_id>/hours/export', views.executor_hours_export, name='executor_hours_export'),
    path('executor/<path:executor_id>/hours', views.executor_hours_detail, name='executor_hours_detail'),
    path('executor/api/<path:executor_id>', views.executor_detail_api, name='executor_detail_api'),
    path('executor/<path:executor_id>', views.executor_detail, name='executor_detail'),

    # Cities
    path('city', views.city_list, name='city_list'),
    path('city/create', views.city_create, name='city_create'),
    path('city/<int:pk>', views.city_detail, name='city_detail'),
    path('city/<int:pk>/update', views.city_update, name='city_update'),
    path('city/<int:pk>/delete', views.city_delete, name='city_delete'),

    # City Files
    path('city/file', views.city_file_list, name='city_file_list'),
    path('city/file/create', views.city_file_create, name='city_file_create'),
    path('city/file/<int:pk>/parse', views.city_file_parse, name='city_file_parse'),

    # Cities
    path('OFC', views.ofc_list, name='ofc_list'),
    path('OFC/create', views.ofc_create, name='ofc_create'),
    path('OFC/<int:pk>', views.ofc_detail, name='ofc_detail'),
    path('OFC/<int:pk>/update', views.ofc_update, name='ofc_update'),
    path('OFC/<int:pk>/delete', views.ofc_delete, name='ofc_delete'),

    # Bicycle
    path('bicycle', views.bicycle_list, name='bicycle_list'),
    path('bicycle/create', views.bicycle_create, name='bicycle_create'),
    path('bicycle/<int:pk>', views.bicycle_detail, name='bicycle_detail'),
    path('bicycle/<int:pk>/update', views.bicycle_update, name='bicycle_update'),
    path('bicycle/<int:pk>/delete', views.bicycle_delete, name='bicycle_delete'),

    # Transport
    path('transport', views.transport_list, name='transport_list'),

    # Citizenship
    path('citizenship', views.citizenship_list, name='citizenship_list'),
    path('citizenship/create', views.citizenship_create, name='citizenship_create'),
    path('citizenship/<int:pk>', views.citizenship_detail, name='citizenship_detail'),
    path('citizenship/<int:pk>/update', views.citizenship_update, name='citizenship_update'),
    path('citizenship/<int:pk>/delete', views.citizenship_delete, name='citizenship_delete'),

    # Citizenship types
    path('citizenship/type', views.citizenship_type_list, name='citizenship_type_list'),
    path('citizenship/type/create', views.citizenship_type_create, name='citizenship_type_create'),
    path('citizenship/type/<int:pk>', views.citizenship_type_detail, name='citizenship_type_detail'),
    path('citizenship/type/<int:pk>/update', views.citizenship_type_update, name='citizenship_type_update'),
    path('citizenship/type/<int:pk>/delete', views.citizenship_type_delete, name='citizenship_type_delete'),

    # Archive files
    path('archive', views.archive_file_list, name='archive_file_list'),
    path('archive/create', views.archive_file_create, name='archive_file_create'),
    path('archive/<int:pk>', views.archive_file_detail, name='archive_file_detail'),
    path('archive/<int:pk>/status', views.archive_file_get_status, name='archive_file_get_status'),
    path('archive/<int:pk>/update', views.archive_file_update, name='archive_file_update'),
    path('archive/<int:pk>/delete', views.archive_file_delete, name='archive_file_delete'),

    path('calculate', views.home, name='calculate'),
]
