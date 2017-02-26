import string
from django.core.exceptions import  ValidationError
class CustomPasswordValidator(object):
    """
      Validate whether the password is combination of Upper case, Lower case, digit and special char.
    """

    def validate(self, password, user=None):
        invalid = True
        if any((c in password) for c in string.digits) and any((c in password) for c in string.lowercase) \
                and any((c in password) for c in string.uppercase) and any((c in password) for c in string.punctuation):
            invalid=False

        if invalid:
            raise ValidationError(
                "Your password must contain at least one number, one upper case," \
               " one lower case and one special character.",
                code='invalid_password_set',
            )

    def get_help_text(self):
        return "Your password must contain at least one number, one upper case," \
               " one lower case and one special character."