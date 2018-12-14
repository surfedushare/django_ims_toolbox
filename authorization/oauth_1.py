from oauthlib.oauth1 import RequestValidator

from django.contrib.auth.backends import RemoteUserBackend

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
        This function always returns True, because this check is unnecessary in our case.
        Usually a request validation happens in two steps.
        The consumer asks to login. The client acknowledges by distributing a "nonce" (a one use token).
        This nonce should be checked if indeed nobody has used the nonce before.
        However in the LTI protocol a "launch" is initiated by the consumer in one go.
        Therefor we can not secure these requests with a nonce.
        To mitigate risks the launch should always happen over SSL.

        :param client_key:
        :param timestamp:
        :param nonce:
        :param request:
        :param request_token:
        :param access_token:
        :return:
        """
        return True

    def check_nonce(self, nonce):
        """
        Not checking nonce validity. See validate_timestamp_and_nonce docstring

        :param nonce:
        :return:
        """
        return True


class LTIRemoteUserBackend(RemoteUserBackend):

    def authenticate(self, request, remote_user):
        user = super().authenticate(request, remote_user)
        if not user.first_name or not user.last_name:  # because RemoteUserBackend.configure_user ignores request :(
            user.first_name = request.POST.get('lis_person_name_given', '')
            user.last_name = request.POST.get('lis_person_name_family', '')
            user.save()
        return user
