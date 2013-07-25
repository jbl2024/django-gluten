"""django.contrib.auth.tokens, but without using last_login in hash"""

from datetime import date
from django.conf import settings
from django.utils.http import int_to_base36, base36_to_int
from django.core.cache import cache
import random
import string

import logging
logger = logging.getLogger("gluten")


class TokenGenerator(object):

    """
    Strategy object used to generate and check tokens
    """

    TOKEN_TIMEOUT_DAYS = getattr(settings, "TOKEN_TIMEOUT_DAYS", 7)

    def make_token(self, user):
        """
        Returns a token for a given user
        """
        return self._make_token_with_timestamp(user, self._num_days(self._today()))

    def check_token(self, user, token):
        """
        Check that a token is correct for a given user.
        """
        # Parse the token
        try:
            ts_b36, hash, random_string = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        if self._make_token_with_timestamp(user, ts, random_string) != token:
            return False

        # Check the timestamp is within limit
        if (self._num_days(self._today()) - ts) > self.TOKEN_TIMEOUT_DAYS:
            return False

        # Check for random string
        if random_string != cache.get('%.random' % user.username, ''):
            return False

        return True

    def invalidate_token(self, user):
        cache.delete('%s.random' % user.username)

    def _make_token_with_timestamp(self, user, timestamp, random_string=None):
        # timestamp is number of days since 2001-1-1.  Converted to
        # base 36, this gives us a 3 digit string until about 2121
        ts_b36 = int_to_base36(timestamp)

        if random_string is None:
            random_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(64))
        cache.set('%s.random' % user.username, random_string, TokenGenerator.TOKEN_TIMEOUT_DAYS*86400)

        # No longer using last login time
        from django.utils.hashcompat import sha_constructor
        hash = sha_constructor(settings.SECRET_KEY + unicode(user.username) +
                               user.password +
                               unicode(timestamp)).hexdigest()[::2]
        return "%s-%s-%s" % (ts_b36, hash, random_string)

    def _num_days(self, dt):
        return (dt - date(2001, 1, 1)).days

    def _today(self):
        # Used for mocking in tests
        return date.today()


token_generator = TokenGenerator()
