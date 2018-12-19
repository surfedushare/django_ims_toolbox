from oauthlib.oauth1 import RequestValidator

from django.contrib.auth.backends import RemoteUserBackend
from django.core.exceptions import ValidationError
from social_django.models import Nonce

from ims.models import LTITenant


class LTIRequestValidator(RequestValidator):
    """
    A RequestValidator to validate the launch of a token.
    The security of this RequestValidator is low and should not be used for normal OAuth flows.
    Review the validate_timestamp_and_nonce method for more information on the weaknesses in security of LTI.
    """

    @property
    def client_key_length(self):
        return 20, 36  # adjusted to accept UUID

    @property
    def safe_characters(self):
        safe_characters = super().safe_characters
        safe_characters.add("-")
        return safe_characters

    def get_client_secret(self, client_key, request):
        credentials = LTITenant.objects.get(client_key=client_key)
        return credentials.client_secret

    def validate_client_key(self, client_key, request):
        try:
            LTITenant.objects.get(client_key=client_key)
            return True
        except LTITenant.DoesNotExist:
            return False

    def validate_timestamp_and_nonce(self, client_key, timestamp, nonce,
                                     request, request_token=None, access_token=None):
        """
        To prevent replay attacks we need to check whether the nonce has not been used before for client and time
        The Nonce has a unique_together on all its fields and should raise when the Nonce was created before
        As fallback there is also the created variable which should always be True
        """
        try:
            nonce, created = Nonce.objects.get_or_create(timestamp=timestamp, salt=nonce, server_url=client_key)
        except ValidationError:
            return False
        return created


class LTIRemoteUserBackend(RemoteUserBackend):

    def authenticate(self, request, remote_user):
        user = super().authenticate(request, remote_user)
        if not user.first_name or not user.last_name:  # because RemoteUserBackend.configure_user ignores request :(
            user.first_name = request.POST.get('lis_person_name_given', '')
            user.last_name = request.POST.get('lis_person_name_family', '')
            user.save()
        return user
