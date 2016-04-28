import re
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404

from app.forms import ProjectForm, ProfileForm, AccountUpdateForm
from app.models import Request, Offer, UserProfile, Notification, RequestCategory, RequestSubCategory, SkillTag, Rating

# ------------------------------------------------------------------
# Project/Request Views
# ------------------------------------------------------------------

'''
    users will be able to rate 0 - 5 stars for specific project
    reputation will be calculated as rating*RATING_FACTOR
    ex: 3.5 star will result 35 reputation points
'''
# Reputation Rules
REQUEST_ACCEPTED_REPUTATION_POINT = 10
OFFERING_REPUTATION_POINT = 2
RATING_FACTOR_REPUTATION_POINT = 10


@login_required()
def edit_view(request, slug):
    instance = get_object_or_404(Request, slug=slug)
    category = None
    if request.method == 'POST':
        type = request.POST['type']
        if type:
            category = get_object_or_404(RequestCategory, slug=type)
        form = ProjectForm(request.POST or None, instance=instance)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            if category:
                project.type = category

            project.save()
            for id in request.POST.getlist('skills'):
                tag = SkillTag.objects.get(pk=id)
                if tag:
                    project.skills.add(tag)

            project.save()
            messages.add_message(request, messages.SUCCESS, 'Your Request has been updated!')
            return HttpResponseRedirect("/projects/" + str(project.slug) + "/")
        else:
            print form.errors
    else:
        form = ProjectForm()
    return render(request=request, template_name='app/editProject.html', context={'form': form, 'instance': instance})


@login_required()
def delete_view(request, slug):
    project = get_object_or_404(Request, slug=slug)
    if project.created_by == request.user:
        project.delete()
        messages.add_message(request, messages.SUCCESS, 'Your Request has been Deleted!')
        return HttpResponseRedirect("/dashboard/")


# @login_required()
def detail_view(request, slug):
    # todo is slug unique? if not MultipleObjectsReturned will raise
    project = get_object_or_404(Request, slug=slug)

    # ratings
    ratings = Rating.objects.filter(project=project)

    if request.user.is_authenticated():
        template='app/details.html'
        num_notifications = get_notifications(request)
        return render(request=request, template_name=template,
                  context={'project': project, 'num_notifications': num_notifications, 'ratings': ratings})

    else:
        template='app/project_detail.html'
        return render(request=request, template_name=template,
                  context={'project': project,})






# @login_required()
def explore(request):
    # TODO: count project and users on each category for statistics
    # mobile_projects=Request.objects.filter(type=RequestCategory(name='mobile')).count()
    # catagory_stastics={'mobile':[12,5],'writing':[12,5],'data-entry':[12,5],'mobile':[12,5],'mobile':[12,5]}

    if request.user.is_authenticated():
        template='app/project_showcase-auth.html'

    else:
        template='app/project_showcase.html'

    result_projects = Request.objects.all()
    return render(request=request, template_name=template, context={'projects': result_projects})


@login_required()
def change_project_status(request):
    if request.method == 'GET':
        project_id = request.GET['project_id']
        new_status = request.GET['project_status']

        valid_statuses = [100, 101, 102]  # todo remove this magic numbers put them some global pos with cool name

        # todo validate new_status
        # if not new_status in valid_statuses:
        #     return HttpResponse('Bad request: No such project status!')

        project = get_object_or_404(Request, pk=project_id)

        redirect_url = "/projects/" + str(project.slug) + "/"

        # check if project is already completed
        old_status = project.status
        if old_status == 101:  # Complete status is irreversible
            response = {'status': 0, 'message': redirect_url}
            messages.add_message(request, messages.SUCCESS, 'Project is already done!')
            return JsonResponse(response)

        # check if he has edit privilege
        if project.created_by != request.user:
            response = {'status': 0, 'message': redirect_url}
            return JsonResponse(response)

        if int(new_status) == 101:
            # ask for collaborator review
            project.status = new_status
            project.save()
            if project.collaborators:
                queryset = project.collaborators.all()
                queryset = serializers.serialize('json', queryset, fields=('username', 'first_name'))
                # return HttpResponse(queryset, content_type='application/json')
                response = {'status': 1, 'collaborators': queryset}
                messages.add_message(request, messages.SUCCESS, 'Request status updated!')
                return JsonResponse(response)

        project.status = new_status
        project.save()
        response = {'status': 1, 'message': redirect_url}
        messages.add_message(request, messages.SUCCESS, 'Request status updated!')
        return JsonResponse(response)


# ------------------------------------------------------------------
# Search Projects
# ------------------------------------------------------------------

'''
from : http://julienphalip.com/post/2825034077/adding-search-to-a-django-site-in-a-snap
'''


def normalize_query(query_string, findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    '''
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__contains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def search(request):
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        entry_query = get_query(query_string, ['title', 'description', ])
        found_entries = Request.objects.filter(entry_query).order_by('-created')

    return render(request=request, template_name='app/search_results.html',
                  context={'query_string': query_string, 'found_entries': found_entries})


# ------------------------------------------------------------------
# Notification
# ------------------------------------------------------------------

@login_required()
def notifications(request):
    user_notifications = Notification.objects.filter(for_user=request.user)
    for notification in user_notifications:
        notification.is_seen = True
        notification.save()
    user_notifications = Notification.objects.filter(for_user=request.user)

    return render(request=request, template_name='app/notifications.html',
                  context={'notifications': user_notifications})


def get_notifications(request):
    return len(Notification.objects.filter(for_user=request.user, is_seen=False))


# ------------------------------------------------------------------
# Offer , Collaborate
# ------------------------------------------------------------------
@login_required()
def offer(request, slug):


    project = get_object_or_404(Request, slug=slug)
    offered_by = request.user

    # todo validations
    # can't offer my own project
    if(offered_by==project.created_by):
        # messages.add_message(request, messages.INFO, 'Hmmm this is your project!')
        return HttpResponseRedirect("/projects/" + str(slug) + "/")

    # todo check if this user has already sent offer request ...
    sent_request = Offer.objects.filter(project=project, offer_by=offered_by)
    if sent_request:
        messages.add_message(request, messages.INFO, 'Your have already sent offer request for this project!')
        return HttpResponseRedirect("/projects/" + str(slug) + "/")




    # reputation change for offering
    offered_by_profile = UserProfile.objects.get(user=offered_by)
    if offered_by_profile:
        offered_by_profile.reputation += OFFERING_REPUTATION_POINT
        offered_by_profile.save()

    offer = Offer(project=project, offer_by=offered_by)
    offer.save()
    notification = Notification(for_user=project.created_by, extra=offer, type=200, action_url="/projects/" + str(slug),
                                message="You have received an offer ", )
    notification.save()
    # todo show offer processed message and redirect
    messages.add_message(request, messages.SUCCESS, 'Your Offer has been sent!')
    return HttpResponseRedirect("/projects/" + str(slug) + "/")


@login_required
def rejectOffer(request):
    if request.method == 'GET':
        id = request.GET['offer_id']
        offer = Offer.objects.get(pk=id)
        if offer:
            offer.is_seen = True
            offer.save()
            notification = Notification(for_user=offer.offer_by, type=202, action_url="/projects/" + offer.project.slug,
                                        extra=offer, message="Your offer has been rejected.")
            notification.save()
            messages.add_message(request, messages.SUCCESS, 'You have rejected an offer!')
            return HttpResponseRedirect("/projects/" + str(offer.project.slug) + "/")

        else:
            return HttpResponse('Bad request!')


@login_required
def acceptOffer(request):
    if request.method == 'GET':
        id = request.GET['offer_id']
        offer = Offer.objects.get(pk=id)
        if offer:
            offer.is_accepted = True
            offer.is_seen = True
            offer.project.collaborators.add(offer.offer_by)
            offer.save()
            notification = Notification(for_user=offer.offer_by, type=201, action_url="/projects/" + offer.project.slug,
                                        extra=offer, message="Your offer has been accepted.")
            notification.save()

            # update user reputation
            profile = UserProfile.objects.get(user=offer.offer_by)
            profile.reputation += REQUEST_ACCEPTED_REPUTATION_POINT
            profile.save()
            messages.add_message(request, messages.SUCCESS, 'You have accepted an offer!')
            return HttpResponseRedirect("/projects/" + str(offer.project.slug) + "/")

        else:
            return HttpResponse('bad request')


# ------------------------------------------------------------------
# Static
# ------------------------------------------------------------------

def indexView(request):
    testimonials = Request.objects.filter(status=101)[:1]

    if request.user.is_authenticated():
        return HttpResponseRedirect('/dashboard')
    return render(request, 'index.html', context={'testimonial_projects': testimonials})


# ------------------------------------------------------------------
# User,Profile,Dashboard
# ------------------------------------------------------------------

@login_required()
def edit_profile_view(request):
    user_name = request.user.username
    if request.method == 'GET':
        num_notifications = get_notifications(request)
        user = get_object_or_404(User, username=user_name)
        profile = get_object_or_404(UserProfile, user=user)
        user_skills = profile.skills.all()
        user_requests = Request.objects.filter(created_by=user)[:5]
        user_offers = Offer.objects.filter(offer_by=user, is_accepted=True)[:5]
        requests_count = len(user_requests)
        offers_count = len(user_offers)
        data = {'profile': profile,
                'skills': user_skills,
                'offers': user_offers,
                'requests': user_requests,
                'num_offers': offers_count,
                'num_requests': requests_count,
                }
        return render(request=request, template_name='app/editProfile.html',
                      context={'data': data, 'num_notifications': num_notifications})

    elif request.method == 'POST':
        instance = get_object_or_404(UserProfile, user=request.user)
        form = ProfileForm(request.POST or None, instance=instance)
        if form.is_valid():
            for id in request.POST.getlist('skills'):
                tag = SkillTag.objects.get(pk=id)
                if tag:
                    instance.skills.add(tag)

            instance.save()
            form.save(commit=True)
            messages.add_message(request, messages.SUCCESS, 'Your Profile Updated Successfully !')
            return HttpResponseRedirect('/users/' + str(user_name))

        else:
            return HttpResponseRedirect("/users/" + str(user_name))


@login_required()
def dashboard(request):
    all_suggestable_requests = Request.objects.filter(status=100, publish=True).exclude(created_by=request.user)
    projects_offer_by_user = Offer.objects.filter(offer_by=request.user).values('project').distinct()
    suggestions = all_suggestable_requests.exclude(pk__in=projects_offer_by_user)

    working_on = Offer.objects.filter(offer_by=request.user, is_accepted=True)[:5]
    my_projects = Request.objects.by(request.user)[:5]
    num_notifications = get_notifications(request)

    return render(request=request, template_name='app/dashboard.html',
                  context={'suggestions': suggestions, 'my_projects': my_projects,
                           'num_notifications': num_notifications, 'projects_working_on': working_on})

@login_required()
def users_profile_view(request, user_name):
    num_notifications = get_notifications(request)
    user = get_object_or_404(User, username=user_name)
    profile = get_object_or_404(UserProfile, user=user)
    user_skills = profile.skills.all()
    user_requests = Request.objects.filter(created_by=user)[:5]
    user_offers = Offer.objects.filter(offer_by=user, is_accepted=True)[:5]
    requests_count = len(user_requests)
    offers_count = len(user_offers)

    data = {'profile': profile,
            'skills': user_skills,
            'offers': user_offers,
            'requests': user_requests,
            'num_offers': offers_count,
            'num_requests': requests_count,
            }

    return render(request=request, template_name='app/profile.html',
                  context={'data': data, 'num_notifications': num_notifications})


# ------------------------------------------------------------------
# AJAX
# ------------------------------------------------------------------

@login_required()
def get_project_types(request):
    # TODO: WARNING:: validate query parameter
    if request.GET:
        q = request.GET['q']
        category = get_object_or_404(RequestCategory, slug=q)
        queryset = category.sub_categories.all()
        queryset = serializers.serialize('json', queryset, fields=('name', 'slug'))
        return HttpResponse(queryset, content_type='application/json')
    else:
        return HttpResponse('bad request')


@login_required()
def get_skill_tags(request):
    if request.GET:
        q = request.GET['q']
        sub_catagory = get_object_or_404(RequestSubCategory, slug=q)
        queryset = sub_catagory.skill_tags.all()
        queryset = serializers.serialize('json', queryset, fields=('name',))
        return HttpResponse(queryset, content_type='application/json')


@login_required()
def get_project_categories(request):
    queryset = RequestCategory.objects.all()
    queryset = serializers.serialize('json', queryset, fields=('name',))
    return HttpResponse(queryset, content_type='application/json')


@login_required()
def account_edit(request):
    if request.method == 'POST':
        form = AccountUpdateForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save(commit=True)
            messages.add_message(request, messages.SUCCESS, 'Your Account Updated Successfully !')
            return HttpResponseRedirect("/dashboard")  # todo use reverse
        else:
            print form.errors
    else:
        form = AccountUpdateForm()

    return render(request=request, template_name='app/account_setting.html', context={'form': form})


def get_tags(request):
    if request.GET:
        q = request.GET['q']
        queryset = SkillTag.objects.filter(name__startswith=q)
        queryset = serializers.serialize('json', queryset, fields=('name',))
        return HttpResponse(queryset, content_type='application/json')


def filter_project(request):
    if request.GET:
        category = request.GET['category']
        job = request.GET['job']  # todo: do something about this
        skills = request.GET.getlist('skills[]')

        # TODO - validate query parameters
        category_obj = None
        if category != -1:
            try:
                category_obj = RequestCategory.objects.get(slug=category)
            except RequestCategory.DoesNotExist:
                category_obj = None

        skill_tags = []
        if len(skills) > 0:
            for id in request.GET.getlist('skills[]'):  # TODO FIXME
                try:
                    tag = SkillTag.objects.get(pk=id)
                    if tag:
                        skill_tags.insert(0, tag)
                except SkillTag.DoesNotExist:
                    pass

        result = []

        if category_obj and skill_tags:
            temp = Request.objects.filter(~Q(created_by=request.user), type=category_obj, status=100, )

            if temp:
                result = temp.filter(skills__in=skill_tags)
                if not result:
                    result = temp
            else:
                result = Request.objects.filter(skills__in=skill_tags)  # only by skills

        if category_obj and not skill_tags:
            result = Request.objects.filter(type=category_obj)  # only by category
        if skill_tags and not category_obj:
            result = Request.objects.filter(skills__in=skill_tags)  # only by skills

        result = result.filter(status=100).exclude(created_by=request.user)

        projects_offer_by_user = Offer.objects.filter(offer_by=request.user).values('project').distinct()

        result = result.exclude(pk__in=projects_offer_by_user)


        # FIXME :: todo plus filter offer that are already sent.

        queryset = serializers.serialize('json', result)
        return HttpResponse(queryset, content_type='application/json')

    else:
        return HttpResponse('bad request')


@login_required()
def get_project(request):
    if request.GET:
        q = request.GET['q']
        project = get_object_or_404(Request, pk=q)
        array_result = serializers.serialize('json', [project], ensure_ascii=False)
        project = array_result[1:-1]
        return HttpResponse(project, content_type='application/json')


@login_required()
def project_create(request):
    # todo there is no validation here and... BETTER TO POST DATA WITH POST REQUEST FOLLOWING THE REST CONVENTION
    if request.POST:
        if request.is_ajax():
            title = request.POST.get('title')
            category_name = request.POST.get('category')
            description = request.POST.get('description')
            skills = request.POST.getlist('skills[]')

            category = None
            request_instance = None
            if category_name:
                category = get_object_or_404(RequestCategory, slug=category_name)

            if title and category:
                request_instance = Request(title=title, created_by=request.user)
                request_instance.save()
                request_instance.type = category
                request_instance.save()
            if skills and request_instance:
                for id in skills:
                    tag = SkillTag.objects.get(pk=id)
                    if tag:
                        request_instance.skills.add(tag)
            if description and request_instance:
                request_instance.description = description

            if request_instance:
                request_instance.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error'})

    else:
        return HttpResponseRedirect("/dashboard/")


@login_required()
def create_request_offer(request):
    # todo there is no validation here

    if request.POST:
        if request.is_ajax():

            offer_id = request.POST.get('offer_id')

            # OFFER
            if offer_id:
                offer_project = Request.objects.get(pk=offer_id)
                offer_instance = Offer(project=offer_project, offer_by=request.user)
                offer_instance.save()

                # reputation change for offering
                offered_by_profile = UserProfile.objects.get(user=request.user)
                if offered_by_profile:
                    offered_by_profile.reputation += OFFERING_REPUTATION_POINT
                    offered_by_profile.save()

                notification = Notification(for_user=offer_project.created_by, extra=offer_instance, type=200,
                                            action_url="/projects/" + str(offer_project.slug),
                                            message="You have received an offer ", )
                notification.save()

            # REQUEST
            return project_create(request)

        else:
            return HttpResponseRedirect("/dashboard/")


    else:
        return HttpResponseRedirect("/dashboard/")


@login_required()
def rate_user(request):
    # get user to be rated and project
    project = None
    score = None
    comment = None
    user_to_rate = project.created_by
    actor = request.user

    if (project.created_by == actor):  # user has rating privilege only for his/her project
        if (actor != user_to_rate):  # can't rate self
            rate = Rating(score=score, comment=comment, rated_user=user_to_rate, project=project)
            rate.save()


# @login_required()
def filter_projects(request, category_name):
    catagory = get_object_or_404(RequestCategory, slug=category_name)
    result_projects = Request.objects.filter(type=catagory)

    if request.user.is_authenticated():
        template='app/explore_auth.html'

    else:
        template='app/explore.html'

    return render(request=request, template_name=template,
                  context={'projects': result_projects, 'category': catagory.name})
