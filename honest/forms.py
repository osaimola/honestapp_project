from django import forms
from honest.models import Category, Area, Person, UserProfile


class CategoryForm(forms.ModelForm):
    category = forms.CharField(max_length=100, help_text='Enter the category name. EG Tailor, Mechanic')
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Category
        fields = ('category',)


class AreaForm(forms.ModelForm):
    state = forms.CharField(max_length=100, help_text='Enter the State name. EG Lagos, Kaduna')
    views = forms.IntegerField(widget=forms.HiddenInput, required=False)
    slug = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Area
        fields = ('state',)


class PersonForm(forms.ModelForm):
    # define forms for adding new service and location, other fields will be populated automatically
    new_service = forms.CharField(max_length=100, required=False, help_text="Enter their service ONLY if it IS NOT "
                                                                            "found above, EG Web Developer, Mechanic")
    new_location = forms.CharField(max_length=100, required=False, help_text="Enter their location ONLY if it IS NOT"
                                                                             " found above, EG Lagos, Kaduna")

    class Meta:
        # point form to this model to populate all its fields
        model = Person
        # exclude fields which users should not be able to influence/interact with
        exclude = ('date_added', 'views', 'upvotes', 'downvotes',)

    def __init__(self, *args, **kwargs):
        # override init to make service and location fields optional
        # we will later check if an existing or a new value was used and handle accordingly
        super(PersonForm, self).__init__(*args, **kwargs)
        self.fields['service'].required = False
        self.fields['location'].required = False

    def clean(self):
        service = self.cleaned_data.get('service')
        new_service = self.cleaned_data.get('new_service')
        location = self.cleaned_data.get('location')
        new_location = self.cleaned_data.get('new_location')
        if not service and not new_service:
            # no service was specified
            raise forms.ValidationError("Must choose what service they provide or specify a new one")
        elif not service:
            # get or create checks existing categories, if none, create new category and set person service to this.
            service, created = Category.objects.get_or_create(category=new_service)
            self.cleaned_data['service'] = service
        if not location and not new_location:
            # no location specified
            raise forms.ValidationError("Must choose an existing location or specify a new one")
        elif not location:
            # get or create checks the existing areas, if no matching one is found, it creates a new one and sets the
            # person location to the new created location
            location, created = Area.objects.get_or_create(state=new_location)
            self.cleaned_data['location'] = location

        return super(PersonForm, self).clean()


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = UserProfile
        fields = ('username', 'first_name', 'email', 'password')
