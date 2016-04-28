from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify
from app.models import Request


class TestRequest(TestCase):

    # tests creating a request with just a title
    def test_create_request_rapidly(self):
        author = User(username='test_user')
        author.save()
        title = "hello world"
        request = Request(title=title, created_by=author)
        request.save()
        all_requests = Request.objects.all()
        self.assertEquals(len(all_requests), 1)  # assert there is only one request
        self.assertEquals(request, all_requests[0])  # assert this is the first request
        self.assertEquals(request.title, title)  # assert title
        self.assertEquals(request.slug, slugify(title))  # assert slug
        self.assertEquals(request.created_by, author)  # assert author
        self.assertEquals(request.status, 100)  # default status is opened STATUS_OPENED=100
        self.assertEquals(request.created.day, timezone.now().day)  # posted today
        self.assertEquals(request.publish, True)  # default is published
        self.assertSequenceEqual(request.collaborators.all(), [])  # assert there are no collaborators
        self.assertSequenceEqual(request.skills.all(), [])  # assert skills are empty
        self.assertEquals(request.type, None)  # assert type in not specified

    def test_create_request_with_details(self):
        author = User(username='test_user')
        author.save()
        title = "hello world"
        description = "hello world"
        request = Request(title=title, description=description, requested_by=author)
        request.save()

    def test_publish_request(self):
        pass

    def test_edit_request(self):
        pass

    def test_delete_request(self):
        pass


class TestOffer(TestCase):
    pass


class TestNotification(TestCase):
    pass


class TestUser(TestCase):
    pass


class TestUserProfile(TestCase):
    pass
