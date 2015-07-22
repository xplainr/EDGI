from rauth import OAuth2Service
from rauth.session import OAuth2Session

from django.conf import settings
import json

def get_oauth_service():
	return OAuth2Service (
		client_id = settings.SM_CLIENT_ID,
		client_secret= settings.SM_SECRET,
		name = 'surveymonkey',
		authorize_url = 'https://api.surveymonkey.net/oauth/authorize',
		base_url = 'https://api.surveymonkey.net',
		access_token_url = 'https://api.surveymonkey.net/oauth/token?api_key=%s' % settings.SM_API_KEY
	)

def build_api_url(name):
	prekey = 'user' if 'user' in name.lower() else 'surveys'
	# return 'https://api.surveymonkey.net/v2/%s/%s?api_key=%s' % (prekey, name, settings.SM_API_KEY)
	return 'https://api.surveymonkey.net/v2/{}/{}?api_key={}'.format(prekey, name, settings.SM_API_KEY)

def get_oauth_url():
	surveymonkey = get_oauth_service()
	redirect_uri = "http://127.0.0.1:8080/oa2callback"
	params = {
		'redirect_uri': redirect_uri,
		'api_key': settings.SM_API_KEY,
		'response_type': 'code'
	}
	url = surveymonkey.get_authorize_url(**params)
	return url

def get_session_from_response(request):
	service = get_oauth_service()
	return service.get_auth_session(
		data = {
			'code': request.GET['code'], 
			'grant_type': 'authorization_code',
			'redirect_uri': 'http://127.0.0.1:8080/oa2callback'
		},
		decoder=json.loads
	)

def get_session_from_user(user):
	service = get_oauth_service()
	session = OAuth2Session(client_id = settings.SM_CLIENT_ID, client_secret=settings.SM_SECRET, access_token=user.access_token, service=service)
	return session

def sm_request(session, method, body):
	encoded_response = session.post(build_api_url(method), 
		                         params={'format': 'json'}, 
		                         data=json.dumps(body),
		                         headers={'content-type': 
		                                  'application/json'})
	try:
		response = encoded_response.json()
		if response['status'] != 0:
			response = None
	except:
		response = None
	print(response)
	return response