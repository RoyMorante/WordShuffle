from django.urls import path
from . import views

urlpatterns = [
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/generate-qr/', views.staff_generate_qr, name='staff_generate_qr'),
    path('staff/vote/', views.staff_vote_page, name='staff_vote_page'),
    path('staff/validate-viewer/', views.validate_viewer_for_vote, name='validate_viewer'),
    path('staff/submit-vote/', views.staff_submit_vote, name='staff_submit_vote'),
    path('staff/live/', views.live_dashboard, name='live_dashboard'),
    path('staff/retrieve-qr/', views.staff_retrieve_qr, name='staff_retrieve_qr'),
    path('staff/raffle-control/', views.staff_raffle_control, name='staff_raffle_control'),
    path('staff/raffle-draw/', views.raffle_draw_page, name='raffle_draw_page'),
    path('staff/raffle-spin/', views.raffle_spin, name='raffle_spin'),
]