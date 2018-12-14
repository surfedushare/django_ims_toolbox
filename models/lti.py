import uuid
from oauthlib.common import generate_token

from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse

from datagrowth.configuration import ConfigurationField
from canvas.constants import CanvasVisibility  # TODO: get rid of this dependency


class LTIPrivacyLevels(object):
    ANONYMOUS = 'anonymous'
    EMAIL_ONLY = 'email_only'
    NAME_ONLY = 'name_only'
    PUBLIC = 'public'


PRIVACY_LEVEL_CHOICES = tuple([
    (value, value) for attr, value in sorted(LTIPrivacyLevels.__dict__.items()) if not attr.startswith('_')
])


VIEW_CHOICES = (
    ('share:common-cartridge-upload', 'Common Cartridge upload'),
    ('share:common-cartridge-fetch', 'Common Cartridge fetch'),
)


class LTIApp(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True)
    view = models.CharField(max_length=50, choices=VIEW_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    title = models.CharField(max_length=128)
    description = models.TextField()
    privacy_level = models.CharField(max_length=50, choices=PRIVACY_LEVEL_CHOICES)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'LTI app'
        verbose_name_plural = 'LTI apps'


class LearningManagementSystems(object):
    CANVAS = 'canvas'
    MOODLE = 'moodle'


LMS_CHOICES = tuple([
    (value, value) for attr, value in sorted(LearningManagementSystems.__dict__.items()) if not attr.startswith('_')
])


class LTITenant(models.Model):

    app = models.ForeignKey(LTIApp)
    organization = models.CharField(max_length=256)
    slug = models.SlugField()
    lms = models.CharField(max_length=256, choices=LMS_CHOICES)  # learning management system
    config = ConfigurationField(default={}, blank=True, namespace='ims', config_defaults={
        'ims_canvas_course_navigation_visibility': CanvasVisibility.ADMINS
    })

    client_key = models.UUIDField('consumer key', primary_key=True, default=uuid.uuid4, editable=False, )
    client_secret = models.CharField('shared secret', max_length=30, default=generate_token, editable=False)
    api_key = models.CharField(max_length=255, null=True, blank=True)
    api_secret = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def _start_generic_session(self, launch_request, data):
        launch_request.session['roles'] = ''
        launch_request.session['api_domain'] = None
        launch_request.session['course_id'] = None

    def _start_canvas_session(self, launch_request, data):
        launch_request.session['roles'] = data.get('roles', '')
        launch_request.session['api_domain'] = data.get('custom_canvas_api_domain', None)
        launch_request.session['course_id'] = data.get('custom_canvas_course_id', None)

    def start_session(self, launch_request, data):
        launch_request.session['tenant_key'] = str(self.client_key)
        if self.lms == LearningManagementSystems.CANVAS:
            self._start_canvas_session(launch_request, data)
        else:
            self._start_generic_session(launch_request, data)

    def get_lti_config_url(self):
        return "{}{}".format(settings.DEFAULT_DOMAIN, reverse('lti-config', args=(self.app.slug, self.slug,)))
    get_lti_config_url.short_description = 'Config URL'

    def __str__(self):
        return '{} ({})'.format(self.organization, self.app)

    class Meta:
        verbose_name = 'LTI tenant'
        verbose_name_plural = 'LTI tenant'
