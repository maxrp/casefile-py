# Copyright (C) 2017-2019 Max R.D. Parmer
# License AGPLv3+: GNU Affero GPL version 3 or later.
# http://www.gnu.org/licenses/agpl.html
'''
Definitions of Exception types and associated helpers.
'''
from sys import exit as sys_exit


class IncompleteCase(Exception):
    '''A case creation was requested, with incomplete information.'''


def err(message, code):
    '''Take a message to present to the user, and exit with the error code.'''
    print("\n ** ", message, "\n")
    sys_exit(code)
