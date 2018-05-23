#!/usr/bin/python

import os
import sys
import logging
import argparse

# Define error codes
ERROR_CODE_GERRIT_LOGIN_FAILURE     =   1
ERROR_CODE_GERRIT_LOGOUT_FAILURE    =   2

class ClassTemplate():
    def __init__(self, logLevel='DEBUG'):
        self.logger = logging.getLogger(__name__)
        self.configLogger(logLevel)

        self.__loadPredefinedParamsFromFile()
        self.__initRestClient()

    def configLogger(self, logLevel):
        GlogFormat  = ('%(module)-15s [%(levelname)-.1s] %(asctime)s'
            + ' [%(lineno)3d] %(message)s')
        dateFormat = '%Y-%m-%d %H:%M:%S'
        logging.basicConfig(level=logLevel,
            format=logFormat,
            datefmt=dateFormat)

    def __loadPredefinedParamsFromFile(self):
        """
        Load predefined parameters from a Python script.
        """
        import utils.buildparams

        self.JOB_SID_MAPPING = eval('utils.buildparams.SH_JOB_SID_MAPPING')

    def __initRestClient(self):
        from utils.authconfig import SH_GERRIT_HTTP_HOST
        from utils.authconfig import SH_GERRIT_HTTP_USER
        from utils.authconfig import SH_GERRIT_HTTP_PASSWD
        from utils.gerritrestapi import GerritRestClient

        self.grClient = GerritRestClient(SH_GERRIT_HTTP_HOST,
            SH_GERRIT_HTTP_USER,
            SH_GERRIT_HTTP_PASSWD)

    def performPreBuildActions(self):
        if not self.grClient.login():
            self.logger.error('Fail to login Gerrit server: %s' %
                self.grClient.getServerUrl())
            sys.exit(ERROR_CODE_GERRIT_LOGIN_FAILURE)

        self.logger.info('Login Gerrit server: %s' %
            self.grClient.getServerUrl())

    def performPostBuildActions(self):
        if not self.jrClient.logout():
            self.logger.warning('Although fail to logout Jenkins,'
                ' the result is acceptable.')

        self.logger.info('Logout Gerrit server: %s' %
            self.grClient.getServerUrl())

    def queryGerritChanges(self, changeBundle, patchsetNumber):
        pass

def parse_options():
    parser = argparse.ArgumentParser(
        description='CI Build Toolkit',
        epilog='Note: Python 2.7.x required.',
        formatter_class=argparse.RawTextHelpFormatter,
        conflict_handler='resolve')

    parser.add_argument('-n', '--dry-run', dest='dry_run',
        action='store_true',
        default=False,
        help='Dryrun mode, do not post comment to Gerrit.')

    parser.add_argument('--log-level', dest='log_level',
        action='store',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Specify logging level.')

    # Option --action only takes valid element from given list as argument
    parser.add_argument('--action', dest='action',
        action='store',
        required=True,
        default=None,
        choices=['kickoff-dev', 'abort-dev', 'store-dev',
            'update-dev', 'post-dev', 'setdesc-dev'],
        help='Specify an action to be performed.')

    # Option --change-bundle takes a list as argument
    parser.add_argument('--change-bundle', dest='change_bundle',
        action='store',
        nargs='+',
        help='Provide change number of Gerrit changes.')

    parser.add_argument('--patchset-number', dest='patchset_number',
        action='store',
        type=int,
        default=0,
        help='Provide patchset number of Gerrit changes.')

    return parser.parse_args()

def load_utils_package():
    """
    Append utils package in search path so that modules can be imported.

    Notice:
    - This is a dynamic way to specify search path for packages.
    - Modules have to be imported in each function where they are used.
    """

    utilsPackage = 'utils'

    execPath = sys.path[0]
    while True:
        dirs = os.listdir(execPath)
        if utilsPackage in dirs:
            sys.path.append(os.path.join(execPath))
            break
        else:
            execPath = os.path.join(os.path.dirname(os.path.normpath(execPath)))

        # Exit while reaching the root
        if os.path.abspath(execPath) == '/':
            break

def main(options):
    load_utils_package()
    instance = ClassTemplate(options.log_level)
    instance.queryGerritChanges(options.change_bundle,
        options.patchset_number)

if __name__ == '__main__':
    main(parse_options())

# vim: set shiftwidth=4 tabstop=4 expandtab
