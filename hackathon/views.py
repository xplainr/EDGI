from django.shortcuts import render, redirect
from django import http
from django.conf import settings

from .utils import *
from .models import User

def login_page(request):
	oauth_url = get_oauth_url()
	return render(request, 'login.html', {'oauth_url': oauth_url})

def oauth2_callback(request):
	session = get_session_from_response(request)
	access_token = session.access_token

	response_data = session.post(build_api_url('get_user_details'), params={'format': 'json'}).json()
	username = response_data['data']['user_details']['username']

	if 'SMSuccessTeam' not in response_data['data']['enterprise_details']['group_name']:
		raise Http404

	try:
		user = User.objects.get(access_token=access_token)
	except User.DoesNotExist:
		user = User.objects.create(username=username, access_token=access_token)

	request.session['at']=access_token

	return redirect('users')

def users_page(request):
	if not 'at' in request.session and not User.objects.filter(access_token=request.session['at']).exists():
		raise http.Http404

	return render(request, 'users.html', {'users': User.objects.all()})

def user_page(request, id=None):
	if not 'at' in request.session and not User.objects.filter(access_token=request.session['at']).exists():
		raise http.Http404

	try:
		user = User.objects.get(id=id)
	except User.DoesNotExist:
		raise http.Http404

	session = get_session_from_user(user)
	response_data = session.post(build_api_url('get_survey_list'), params={'format': 'json'}, data=json.dumps({
		"order_asc": True,
	  	"fields": [
	    	"title",
		    "num_responses",
		    "date_created",
		    "date_modified",
		    "question_count",
		    "language_id",
		    "preview_url"
		  ]	
		}),
		headers={'content-type': 'application/json'}
	).json()

	[
		'English', 'Chinese(Simplified)', 'Chinese(Traditional)', 'Danish', 'Dutch', 'Finnish', 'French', 'German', 'Greek', 
		'Italian', 'Japanese', 'Korean', 'Malay', 'Norwegian', 'Polish', 'Portuguese(Iberian)', 'Portuguese(Brazilian)', 'Russian', 
		'Spanish', 'Swedish', 'Turkish', 'Ukrainian', 'Reverse', 'Albanian', 'Arabic', 'Armenian', 'Basque', 'Bengali', 'Bosnian', 
		'Bulgarian', 'Catalan', 'Croatian', 'Czech', 'Estonian', 'Filipino', 'Georgian', 'Hebrew', 'Hindi', 'Hungarian', 'Icelandic', 
		'Indonesian', 'Irish', 'Kurdish', 'Latvian', 'Lithuanian', 'Macedonian', 'Malayalam', 'Persian', 'Punjabi', 'Romanian', 
		'Serbian', 'Slovak', 'Slovenian', 'Swahili', 'Tamil', 'Telugu', 'Thai', 'Vietnamese', 'Welsh'
	]

	for idx, key in enumerate(response_data.items()):
		print(idx)
	#response_data['data']['surveys'][0]['language_id'] = "English"
	#print(response_data['data']['surveys'][0]['language_id'])


	return render(request, 'user.html', {'surveys': response_data['data']['surveys']})
