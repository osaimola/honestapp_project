from django.test import TestCase
from honest.forms import PersonForm, CategoryForm, AreaForm, UserForm, ReviewsForm
from .models import Category, Area, Person, UserProfile, Review
import datetime


# Create your tests here.
def create_category(category):
    """adds a category"""
    return Category.objects.create(category=category)


def create_area(area):
    """adds an area"""
    return Area.objects.create(state=area)


def create_person(service, location, first_name="Test", last_name="User", phone_number=234567891234,
                  email="tester@yahoo.com", views="", upvotes="", downvotes="", rating=""):
    """creates a new person"""
    if not views and not upvotes and not downvotes and not rating:
        category = create_category(service)
        area = create_area(location)
        return Person.objects.create(service=category, location=area, first_name=first_name, last_name=last_name,
                                     phone_number=phone_number, email=email)
    else:
        category = create_category(service)
        area = create_area(location)
        return Person.objects.create(service=category, location=area, first_name=first_name, last_name=last_name,
                                     phone_number=phone_number, email=email, views=views, upvotes=upvotes,
                                     downvotes=downvotes, rating=rating)


def create_review(person, rating, summary, review_text):
    """creates a new review for a given person"""
    return Review.objects.create(person=person, rating=rating, summary=summary, review_text=review_text)


class CategoryModelTest(TestCase):

    def test_slug_created_with_new_category(self):
        """new categories saved to database should have a slug created from the category name"""
        new_category = create_category("Test Category")
        self.assertEqual(new_category.slug, "test-category")


class AreaModelTest(TestCase):

    def test_slug_created_with_new_area(self):
        """new areas saved to database should have a slug created from the area name"""
        new_area = create_area("Test Area")
        self.assertEqual(new_area.slug, "test-area")


class PersonModelTest(TestCase):

    def test_vote_positive_with_more_upvotes(self):
        """vote positive returns true if more upvotes than downvotes exist"""
        person = create_person(service="Clown", location="Disneyland", views=5, upvotes=10, downvotes=3, rating=5.0)
        self.assertTrue(person.vote_positive())

    def test_vote_positive_with_more_downvotes(self):
        """vote_positive() returns false if more downvotes than upvotes exist"""
        person = create_person(service="Clown", location="Disneyland", views=5, upvotes=4, downvotes=6, rating=5.0)
        self.assertFalse(person.vote_positive())

    def test_set_average_rating_with_reviews(self):
        """set_average_rating() sets the person.rating based on all reviews (sum of ratings/number of reviews)"""
        person = create_person(service="Clown", location="Disneyland", first_name="Psycho")
        create_review(person=person, rating=4.0, summary="Great", review_text="Did a good Job")
        create_review(person=person, rating=5.0, summary="Excellent", review_text="Thoroughly impressed")
        create_review(person=person, rating=2.0, summary="Not Thrilling",
                      review_text="Overly not thrilled by the performance")
        person.set_average_rating()
        self.assertEqual(person.rating, 3.67)

    def test_set_average_rating_without_ratings(self):
        """set_average_rating() should leave person.rating unchanged if no reviews exist"""
        person = create_person(service="Clown", location="Disneyland", first_name="Psycho")
        person.set_average_rating()
        self.assertEqual(person.rating, 0)

    def test_avg_rating_with_no_rating(self):
        """avg_rating() returns 'Not rated yet' when rating does not exist (rating = 0.0)"""
        person = create_person(service="Clown", location="Disneyland", views=5, upvotes=4, downvotes=6, rating=0.0)
        self.assertEqual(person.avg_rating(), "Not Yet Rated")

    def test_avg_rating_with_rating(self):
        """avg_rating() returns the rating when rating > 0.0"""
        person = create_person(service="Clown", location="Disneyland", views=5, upvotes=4, downvotes=6, rating=4.5)
        self.assertEqual(person.avg_rating(), 4.5)


class PeronFormTest(TestCase):

    def test_valid_data_with_new_location_and_service(self):
        """valid person form data should be saved in the correct format"""
        form = PersonForm({
            'new_service': "Clown",
            'new_location': "Disneyland",
            'first_name': "Psycho",
            'last_name': "Bob",
            'phone_number': "012345678912",
            'email': "psychobob@yahoo.com"

        })
        self.assertTrue(form.is_valid())
        person = form.save()
        self.assertEqual(str(person.service), "Clown")
        self.assertEqual(str(person.location), "Disneyland")
        self.assertEqual(person.first_name, "Psycho")
        self.assertEqual(person.last_name, "Bob")
        self.assertEqual(person.phone_number, "012345678912")
        self.assertEqual(person.email, "psychobob@yahoo.com")

    def test_blank_data(self):
        """blank data should render form invalid"""
        form = PersonForm({})
        self.assertFalse(form.is_valid())


class AreaFormTest(TestCase):

    def test_valid_data(self):
        """valid area form data should be saved in the correct format"""
        form = AreaForm({
            'state': "Disneyland",
            'views': 0
        })
        self.assertTrue(form.is_valid())
        area = form.save()
        self.assertEqual(area.state, "Disneyland")
        self.assertEqual(area.views, 0)

    def test_blank_data(self):
        """blank data should render form invalid"""
        form = AreaForm({})
        self.assertFalse(form.is_valid())


class CategoryFormTest(TestCase):

    def test_valid_data(self):
        """valid category form data should be saved in the correct format"""
        form = CategoryForm({
            'category': "Clown",
            'views': 0
        })
        self.assertTrue(form.is_valid())
        category = form.save()
        self.assertEqual(category.category, "Clown")
        self.assertEqual(category.views, 0)

    def test_blank_data(self):
        """blank data should render form invalid"""
        form = CategoryForm({})
        self.assertFalse(form.is_valid())


class UserFormTest(TestCase):

    def test_valid_data(self):
        """valid user form data should be saved in the correct format"""
        form = UserForm({
            'username': "Psychobob",
            'first_name': "Psycho",
            'email': "psychobob@yahoo.com",
            'password': "bobsleighs"
        })
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, "Psychobob")
        self.assertEqual(user.first_name, "Psycho")
        self.assertEqual(user.email, "psychobob@yahoo.com")
        self.assertEqual(user.password, "bobsleighs")

    def test_blank_data(self):
        """blank data should render form invalid"""
        form = UserForm({})
        self.assertFalse(form.is_valid())


class ReviewsFormTest(TestCase):

    def test_valid_data(self):
        """valid review data should be saved in the correct format"""
        person = create_person(service="Clown", location="Disneyland", first_name="Psycho")
        form = ReviewsForm({
            'rating': 5,
            'summary': "Impressive performance",
            'review_text': "Psycho bob really put on a show"
        })
        self.assertTrue(form.is_valid())
        review = form.save(commit=False)
        review.person = person
        review.save()
        self.assertEqual(str(review.person), "Psycho")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.summary, "Impressive performance")
        self.assertEqual(review.review_text, "Psycho bob really put on a show")

    def test_blank_data(self):
        """blank data should render form invalid"""
        form = ReviewsForm({})
        self.assertFalse(form.is_valid())