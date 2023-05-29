from django.shortcuts import render

# Create your views here.
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from google.oauth2 import credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

class GoogleCalendarInitView(View):
    def get(self, request):
        flow = Flow.from_client_secrets_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        request.session['oauth_state'] = state
        return redirect(authorization_url)


class GoogleCalendarRedirectView(APIView):
    def get(self, request):
        state = request.session.pop('oauth_state', '')
        flow = Flow.from_client_secrets_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            state=state,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )
        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        request.session['credentials'] = credentials_to_dict(credentials)
        return redirect(reverse('event-list'))


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }


class EventListView(APIView):
    def get(self, request):
        credentials_dict = request.session.get('credentials')
        if not credentials_dict:
            return Response({'error': 'Authentication credentials not found'}, status=401)

        credentials = credentials.Credentials.from_authorized_user_info(credentials_dict)
        service = build('calendar', 'v3', credentials=credentials)

        events_result = service.events().list(calendarId='primary', maxResults=10).execute()
        events = events_result.get('items', [])

        return Response(events)
