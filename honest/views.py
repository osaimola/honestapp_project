from _datetime import datetime

from django.db.models import F
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from honest.models import Category, Person, Area, Review, UserProfile
from honest.forms import CategoryForm, AreaForm, PersonForm, UserForm, ReviewsForm


# Create your views here.
def index(request):
    category_list = Category.objects.order_by('-views')[:10]
    area_list = Area.objects.order_by('-views')[:10]
    context = {'honest_message': 'We looooove honesty!!',
               'categories': category_list, 'areas': area_list}
    return render(request, 'honest/index.html', context)


def category(request, category_slug):

    # empty dictionary that we can populate later in the class
    context = {}

    try:
        # search for any category with a matching slug
        category = Category.objects.get(slug=category_slug)
        context['category_name'] = category.category

        # get list of all people within this category (ie providing this service)
        people = Person.objects.filter(service=category)
        context['people'] = people
        context['category'] = category

        this_categorys_views = category.views
        context['this_categorys_views'] = this_categorys_views
        count_page_views(request=request, object=category)

        # make empty list of locations and populate with locations people are  in
        areas = []
        for person in people:
            if person.location not in areas:
                areas.append(person.location)
        context['areas'] = areas

    except Category.DoesNotExist:
        # will be handled in template
        pass

    return render(request, 'honest/category.html', context)


def all_categories(request):
    categories = Category.objects.all()
    return render(request, 'honest/all_categories.html', {'categories': categories})


# login required decorator ensures only logged in users can access this page
@login_required()
def add_category(request):
    # if the form type is a http post
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # check if form is valid & save new category if it is
        if form.is_valid():
            form.save(commit=True)

            # take user back to the home page
            return HttpResponseRedirect(reverse('honest:index'))
        else:
            print(form.errors)
    else:
        # if request was not a http post, display the form
        form = CategoryForm()

    return render(request, 'honest/add_category.html', {'form': form})


def area(request, area_slug):
    context = {}
    area = Area.objects.get(slug=area_slug)
    context['area'] = area
    people = Person.objects.filter(location=area)
    context['people'] = people
    this_areas_views = area.views
    context['this_areas_views'] = this_areas_views

    # make empty list of categories and populate with the services people in this area provide
    categories = []
    for person in people:
        if person.service not in categories:
            categories.append(person.service)
    context['categories'] = categories
    count_page_views(request=request, object=area)
    return render(request, 'honest/area.html', context)


def all_areas(request):
    areas = Area.objects.all()
    return render(request, 'honest/all_areas.html', {'areas': areas})


# login required decorator ensures only logged in users can access this page
@login_required()
def add_area(request):
    # if the form type is a http post
    if request.method == 'POST':
        form = AreaForm(request.POST)

        # check if form is valid & save new category if it is
        if form.is_valid():
            form.save(commit=True)

            # take user back to the home page
            return HttpResponseRedirect(reverse('honest:index'))
        else:
            print(form.errors)
    else:
        # if request was not a http post, display the form
        form = AreaForm()

    return render(request, 'honest/add_area.html', {'form': form})


def category_in_area(request, area_slug, category_slug):
    # get the corresponding area and category from the slugs
    category = Category.objects.get(slug=category_slug)
    area = Area.objects.get(slug=area_slug)
    # find all people who have service and location matching the category and area foreign keys provided
    people = Person.objects.filter(service=category, location=area)
    # populate the context with relevant info for the html template
    context = {'category': category, 'area': area, 'people': people}

    return render(request, 'honest/category_in_area.html', context)


def person(request, area_slug, category_slug, person_id):
    this_person = Person.objects.get(pk=person_id)
    if request.method == 'POST':
        form = ReviewsForm(request.POST)

        # save review if form is valid
        if form.is_valid():
            pending_review = form.save(commit=False)
            pending_review.person = Person.objects.get(pk=person_id)
            if request.user.is_authenticated:
                pending_review.reviewer = UserProfile.objects.get(
                    pk=request.user.id)
            pending_review.save()
            this_person.set_average_rating()
            return HttpResponseRedirect(reverse('honest:person', kwargs={'area_slug': area_slug,
                                                                         'category_slug': category_slug,
                                                                         'person_id': person_id}))
        else:
            print(form.errors)
    else:
        context = {'person': this_person}
        this_persons_views = this_person.views
        reviews = Review.objects.filter(person=this_person)
        context['reviews'] = reviews

        form = ReviewsForm()
        context['form'] = form

        count_page_views(request=request, object=this_person)
        #context['visits'] = visits
        context['this_persons_views'] = this_persons_views
        context['area_slug'] = area_slug
        context['category_slug'] = category_slug
        context['person_id'] = person_id
        return render(request, 'honest/person.html', context)


def count_page_views(request, object):
    """this function uses server side cookies to count the views for the object provided
    object model must have a views field which takes an integer"""

    # check if this user has visited this person before
    visits = request.session.get('visits')
    # if user is visiting for first time increment views by 1
    if not visits:
        visits = 1
        object.views = F('views') + 1
        object.save()
    reset_last_visit_time = False
    last_visit = request.session.get('last_visit')
    # if a value for the users last visit does not exist, set the current time to their last visit
    if last_visit:
        last_visit_time = datetime.strptime(
            last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 5:
            # increment the number of views if the last visit was over 5 minutes ago
            visits = visits + 1
            object.views = F('views') + 1
            object.save()
            # and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True
    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits


# login required decorator to ensure only logged in users can access this page
@login_required()
def add_person(request):
    if request.method == 'POST':
        form = PersonForm(request.POST)

        # check if form is valid and & save a new person if it is
        if form.is_valid():
            pending_person = form.save(commit=False)
            pending_person.save()

            # easy fix use commit false, grab user ID, save, use ID to redirect
            return HttpResponseRedirect(reverse('honest:person', kwargs={'area_slug': pending_person.location,
                                                                         'category_slug': pending_person.service,
                                                                         'person_id': pending_person.id}))
        # else:
            # print(form.errors)
    else:
        # if request was not a http post, display form
        form = PersonForm()

    return render(request, 'honest/add_person.html', {'form': form})


def about(request):
    return render(request, 'honest/about.html', {})


def register(request):
    registered = False

    if request.method == 'POST':
        form = UserForm(request.POST)

        if form.is_valid():
            user = form.save()

            user.set_password(user.password)
            user.save()

            registered = True
        else:
            print(form.errors)
    else:
        form = UserForm()

    return render(request, 'honest/register.html', {'form': form, 'registered': registered})


def user_login(request):
    if request.method == 'POST':
        # get username and password from form using POST.get() which returns None if value doesnt exist
        username = request.POST.get('username')
        password = request.POST.get('password')

        # check if login details are valid and return a user object if they are
        user = authenticate(username=username, password=password)

        if user:
            # if user object was returned and user account is active, log them in and take them to homepage
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('honest:index'))

            # if user account is inactive, return error message
            else:
                return HttpResponse('Your account has been disabled, you cannot login.')

        # if no user object then login details are wrong, display error
        else:
            print('Invalid login details provided: {0}, {1}'.format(
                username, password))
            return render(request, 'honest/login.html', {'login_error': 'Either your username or password was incorrect'})

    # if methos is not post, then show template with form
    # no form template because form is handled completely in template as opposed to the modelform method
    else:
        return render(request, 'honest/login.html', {})


# login required decorator to ensure only logged in users can access this page
@login_required()
def user_logout(request):
    # user will always be logged in before reaching here
    logout(request)
    return redirect('honest:index')
