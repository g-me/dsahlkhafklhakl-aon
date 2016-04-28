from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from registration.signals import user_registered


# project status code
STATUS_OPEN = 100
STATUS_DONE = 101
STATUS_CLOSED = 102


class RequestQuerySet(models.QuerySet):
    def published(self):
        return self.filter(publish=True)

    def by(self, requester):
        return self.filter(created_by=requester)

    def opened(self):
        return self.filter(status=STATUS_OPEN)

    def category(self, cat):
        return self.filter(type=cat)


class SkillTag(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "SkillTag"
        verbose_name_plural = "Skill Tags"


class RequestSubCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    skill_tags = models.ManyToManyField(SkillTag, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.slug = slugify(self.name)
        super(RequestSubCategory, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Request Sub Category"
        verbose_name_plural = "Request Sub Categories"


class RequestCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    sub_categories = models.ManyToManyField(RequestSubCategory, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.slug = slugify(self.name)
        super(RequestCategory, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "RequestCategory"
        verbose_name_plural = "Request Categories"


class Request(models.Model):
    PROJECT_STATUS = (
        (STATUS_OPEN, _('Open')),
        (STATUS_DONE, _('Done')),
        (STATUS_CLOSED, _('Closed'))
    )
    title = models.CharField(max_length=200)
    type = models.ForeignKey(RequestCategory, blank=True, null=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    status = models.SmallIntegerField(choices=PROJECT_STATUS, blank=True, default=STATUS_OPEN)
    created_by = models.ForeignKey(User, related_name='requested_by')
    skills = models.ManyToManyField(SkillTag, blank=True, related_name='collaborators')
    collaborators = models.ManyToManyField(User, blank=True)
    publish = models.BooleanField(blank=True, default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # custom query set manager
    objects = RequestQuerySet.as_manager()

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.slug = slugify(self.title)
        super(Request, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = "Request"
        verbose_name_plural = "Requests"
        ordering = ["-created"]


class Offer(models.Model):
    project = models.ForeignKey(Request, null=False, blank=False)
    offer_by = models.ForeignKey(User, null=False, blank=False)
    is_accepted = models.BooleanField(default=False)
    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_rejected(self):
        return not self.is_accepted

    def __str__(self):
        return  self.offer_by.username+" Offerd "+self.project.title+" to "+self.project.created_by.username


class Rating(models.Model):
    project = models.ForeignKey(Request, null=False, blank=False)
    rated_user = models.ForeignKey(User, null=False, blank=False)
    score = models.SmallIntegerField()
    comment = models.CharField(null=False, max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    RECEIVED_OFFER = 200
    OFFER_ACCEPTED = 201
    OFFER_REJECTED = 202

    NOTIFICATION_TYPES = (
        (RECEIVED_OFFER, _('RECEIVED_OFFER')),
        (OFFER_ACCEPTED, _('OFFER_ACCEPTED')),
        (OFFER_REJECTED, _('OFFER_REJECTED')),
    )
    for_user = models.ForeignKey(User, null=False, blank=True)
    action_url = models.URLField(null=False, blank=False)
    type = models.SmallIntegerField(choices=NOTIFICATION_TYPES, blank=True, null=True)
    message = models.CharField(null=False, max_length=200, blank=False)
    is_seen = models.BooleanField(default=False, null=False)
    extra = models.ForeignKey(Offer, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, null=False)
    website = models.URLField(blank=True, null=False, default='')
    stackoverflow_account = models.URLField(blank=True, null=False, default='')
    github_account = models.URLField(blank=True, null=False, default='')
    twitter_account = models.URLField(blank=True, null=False, default='')
    google_plus_account = models.URLField(blank=True, null=False, default='')
    reputation = models.IntegerField(blank=True, null=False, default=0)
    about = models.TextField(blank=True, null=False, default='')
    location = models.CharField(max_length=140, null=False, blank=True, default='')
    career = models.CharField(max_length=140, null=False, blank=True, default='')
    company = models.CharField(max_length=140, null=False, blank=True, default='')
    profileView = models.IntegerField(blank=True, default=0, null=False)
    skills = models.ManyToManyField(SkillTag, blank=True, related_name='skills')

    def __str__(self):
        return self.user.username


def user_registered_callback(sender, user, request, **kwargs):
    profile = UserProfile(user=user)
    profile.save()


user_registered.connect(user_registered_callback)
