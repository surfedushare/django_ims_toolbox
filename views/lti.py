from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.template.response import TemplateResponse
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse, resolve

from lti.contrib.django import DjangoToolProvider

from ims.authorization import LTIRequestValidator
from ims.models import LTIApp, LTIPrivacyLevels, LTITenant
from ims.models.lti import LearningManagementSystems


@csrf_exempt
def lti_launch(request, slug):
    app = get_object_or_404(LTIApp, slug=slug)
    tool_provider = DjangoToolProvider.from_django_request(request=request)
    validator = LTIRequestValidator()
    ok = tool_provider.is_valid_request(validator)
    if not ok:
        return HttpResponseForbidden('The launch request is considered invalid')

    client_key = tool_provider.consumer_key  # request would not be ok if this is not set
    try:
        tenant = app.ltitenant_set.get(client_key=client_key)
    except LTITenant.DoesNotExist:
        return HttpResponseForbidden('{} does not have access to app {}'.format(client_key, app))

    # First thing is to create and login a user, because this influences the session
    if app.privacy_level != LTIPrivacyLevels.ANONYMOUS:
        user = authenticate(request, remote_user=request.POST.get("lis_person_contact_email_primary"))
        if user is not None:
            login(request, user)

    # After we have a user we're gonna set its session based on tenant settings
    # This authorizes a user to use tenant LMS API's
    tenant.start_session(request, request.POST.dict())

    # Lookup the view and return its response
    # Redirect impossible because we need to set cookies for sessions
    url = reverse(app.view)
    view = resolve(url)
    return view.func(request)


def lti_config(request, app_slug, tenant_slug):
    if tenant_slug != app_slug:
        tenant = get_object_or_404(LTITenant, app__slug=app_slug, slug=tenant_slug)
        app = tenant.app
    else:
        tenant = None
        app = get_object_or_404(LTIApp, slug=app_slug)
    return TemplateResponse(request, "ims/lti_config.xml", {
        "host": request.get_host(),
        "app": app,
        "tenant": tenant,
        "lms": LearningManagementSystems
    })


def lti_debug_launch(request, slug):
    app = get_object_or_404(LTIApp, slug=slug)
    client_key = request.GET.get('client_key', None)
    if client_key:
        tenant = app.ltitenant_set.get(client_key=client_key)
    else:
        tenant = LTITenant.objects.last()
    tenant.start_session(request, request.GET.dict())
    if app.privacy_level != LTIPrivacyLevels.ANONYMOUS:
        user = authenticate(request, remote_user=request.GET.get('user', 'debug-user'))
        if user is not None:
            login(request, user)

    # Lookup the view and return its response
    # Redirect impossible because we need to set cookies for sessions
    url = reverse(app.view)
    view = resolve(url)
    return view.func(request)
