
from django.urls import path
from .views import GoogleCalendarInitView, GoogleCalendarRedirectView, EventListView

urlpatterns = [
    path('init/', GoogleCalendarInitView.as_view(), name='calendar-init'),
    path('redirect/', GoogleCalendarRedirectView.as_view(), name='calendar-redirect'),
    path('events/', EventListView.as_view(), name='event-list'),
    # Add the following line
    path('', EventListView.as_view()),  # or replace EventListView with the desired view for rest/v1/calendar/
]

