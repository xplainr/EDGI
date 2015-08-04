from django.shortcuts import render, redirect
from django.http import Http404, HttpRequest
from django.conf import settings
from django.core.exceptions import \
	 ObjectDoesNotExist, PermissionDenied

from .utils import *
from .models import User


def login_page(request):
	oauth_url = get_oauth_url()
	return render(request, 'login.html', {'oauth_url': oauth_url})

def oauth2_callback(request):
	session = get_session_from_response(request)
	access_token = session.access_token

	try:
		response_data = sm_request(session, 'get_user_details', {})
		assert response_data is not None
	except:
		raise IOError('Error retrieving user details from SurveyMonkey.')

	user_details = response_data['data']['user_details']
	enterprise_details = response_data['data'].get('enterprise_details')
	username = user_details['username']
	print user_details
	if user_details['is_enterprise_user']:
		group_name = enterprise_details.get('group_name')
	else:
		raise PermissionDenied(
			'Please login with your SurveyMonkey Enterprise account.')

	if settings.LIMIT_TO_ONE_GROUP:
		groups = User.objects.values('group_name').distinct()
		if len(groups) > 1 or groups[0]['group_name'] != group_name:
			raise PermissionDenied(
				'Only SurveyMonkey accounts in %s group are permitted.' % 
				groups[0]['group_name'])

	try:
		if User.objects.get(is_admin=True, group_name=group_name):
			is_first_group_user = False
	except User.DoesNotExist:
		is_first_group_user = True

	try:
		user = User.objects.get(access_token=access_token, 
			                    group_name=group_name)
	except User.DoesNotExist:
		if is_first_group_user:
			user = User.objects.create(username=username, 
									   access_token=access_token, 
									   is_admin=True, 
									   group_name=group_name)
		else:
			user = User.objects.create(username=username, 
				                       access_token=access_token, 
				                       group_name=group_name)

	request.session['at']=access_token
	request.session['gn']=group_name

	if user.is_admin == True:
		return redirect('users')
	else:
		protocol = 'https://' if request.is_secure() else 'http://'
		return redirect('%ssurveymonkey.com' % protocol)

def users_page(request):
	Users = User.objects.all()

	if \
	'at' not in request.session and \
	not Users.filter(access_token=request.session['at']).exists() and\
	'gn' not in request.session and \
	not Users.filter(group_name=request.session['gn']).exists():
		raise Http404

	ThisUser = Users.filter(access_token=request.session['at']).values()[0]

	if not ThisUser['is_admin']:
		raise PermissionDenied

	if request.method == "POST":
		selected_list = request.POST.get('selected', None)
		add_admin = bool(request.POST.get('add_admin', False))
		remove_admin = bool(request.POST.get('remove_admin', False))
		admin_value = add_admin and not remove_admin
		print bool(admin_value)
		Users.filter(username=selected_list).update(is_admin=admin_value)
		# return render(request, 'users.html')

	print request.method 
	if 'gn' in request.session:
		group_name = request.session['gn']
	else:
		group_name = ThisUser.values()[0]['group_name']

	group_users = User.objects.filter(group_name=group_name)

	return render(request, 'users.html', {'users': group_users,
										  'group_name':group_name,
										  'ThisUsername': ThisUser['username']})

def user_page(request, id=None, survey_title_to_search=''):
	if not 'at' in request.session and \
	   not User.objects.filter(access_token=request.session['at']).exists():
		raise Http404

	try:
		page_string = request.GET.get('page', '1')
		page_int = int(page_string.strip())
		assert isinstance(page_int, int)
		assert page_int > 0
	except:
		page_int = 1

	try:
		user = User.objects.get(id=id)
	except User.DoesNotExist:
		raise Http404

	session = get_session_from_user(user)

	if request.method == "POST":
		survey_title_to_search = request.POST.get('search_value', '')
	else:
		survey_title_to_search = request.session.get('stts','')

	request.session['stts'] = survey_title_to_search

	body = {
			"order_asc": True,
			"page_size" : settings.SURVEY_LIST_PAGE_SIZE,
			"page": page_int,
		  	"fields": [
		  		"title",
			    "num_responses",
			    "date_created",
			    "date_modified",
			    "question_count",
			    "language_id",
			    "preview_url"
			  ]	
			}
	if survey_title_to_search != '':
		body['title'] = survey_title_to_search

	try:
		response_data = sm_request(session,'get_survey_list', body)
		assert response_data is not None
		response_data = response_data['data']
	except:
		raise IOError('Unable to retrieve survey list from SurveyMonkey.')

	language_id_key = [
		'English', 'Chinese(Simplified)', 'Chinese(Traditional)', 'Danish', 'Dutch', 'Finnish', 'French', 'German', 'Greek', 
		'Italian', 'Japanese', 'Korean', 'Malay', 'Norwegian', 'Polish', 'Portuguese(Iberian)', 'Portuguese(Brazilian)', 'Russian', 
		'Spanish', 'Swedish', 'Turkish', 'Ukrainian', 'Reverse', 'Albanian', 'Arabic', 'Armenian', 'Basque', 'Bengali', 'Bosnian', 
		'Bulgarian', 'Catalan', 'Croatian', 'Czech', 'Estonian', 'Filipino', 'Georgian', 'Hebrew', 'Hindi', 'Hungarian', 'Icelandic', 
		'Indonesian', 'Irish', 'Kurdish', 'Latvian', 'Lithuanian', 'Macedonian', 'Malayalam', 'Persian', 'Punjabi', 'Romanian', 
		'Serbian', 'Slovak', 'Slovenian', 'Swahili', 'Tamil', 'Telugu', 'Thai', 'Vietnamese', 'Welsh'
	]

	for idx, response in enumerate(response_data['surveys']):
		response_data['surveys'][idx]['language_id'] = language_id_key[response_data['surveys'][idx]['language_id']-1]

	if page_int > 1:
		prev_link = str(page_int - 1)
	else:
		prev_link = None

	if len(response_data['surveys']) == settings.SURVEY_LIST_PAGE_SIZE:
		next_link = str(page_int + 1)
	else:
		next_link = None

	return render(request, 'user.html', 
		          {'surveys': response_data['surveys'],
		          'prev_link': prev_link,
		          'next_link': next_link,
		          'id': id,
		          'search_value': survey_title_to_search,
		          'page_size': settings.SURVEY_LIST_PAGE_SIZE})
