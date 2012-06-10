'''
directupload upyun backends
'''
import time
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import base64
import hashlib
import os

from base import BaseUploadBackend, json

# AWS Options
FORM_API_KEY        = getattr(settings, 'UPYUN_FORM_API_KEY', None)
BUCKET_NAME         = getattr(settings, 'UPYUN_BUCKET_NAME', None)
ROOT_URL            = 'http://v0.api.upyun.com/'
BUCKET_URL          = getattr(settings, 'UPYUN_BUCKET_URL', ROOT_URL + BUCKET_NAME + '/')
DEFAULT_KEY_PATTERN = getattr(settings, 'UPYUN_DEFAULT_KEY_PATTERN', '{filemd5}{.suffix}')
DEFAULT_FORM_TIME   = getattr(settings, 'UPYUN_DEFAULT_FORM_LIFETIME', 36000) # 10 HOURS


class UpyunBackend(BaseUploadBackend):
    def __init__(self, request, options={}, post_data={}):
        super(UpyunBackend, self).__init__(request, options, post_data)
        self.bucket = self.options.get('bucket', BUCKET_NAME)
        if not FORM_API_KEY:
            raise ImproperlyConfigured("Form api key is a required property.")

        if not self.bucket:
            raise ImproperlyConfigured("Bucket name is a required property.")

    def get_target_url(self):
        return ROOT_URL + BUCKET_NAME + '/'

    def build_options(self):
        self.options['forceIframeTransport'] = True
        self.options['fileObjName'] = 'file'

    def build_post_data(self):
        key = self.options.get('key', DEFAULT_KEY_PATTERN)
        if 'folder' in self.options:
            key = os.path.join(self.options['folder'], key)
        if key[0] != '/':
            key = '/' + key

        policy = {
            'save-key' : key,
            'bucket' : self.bucket,
            'expiration' : int(time.time() + DEFAULT_FORM_TIME)
        }

        policy_string = self.build_post_policy(policy)
        self.policy = base64.b64encode(policy_string).strip()
        self.signature = hashlib.md5(self.policy + '&' + FORM_API_KEY).hexdigest()
        self.post_data['policy'] = self.policy
        self.post_data['signature'] = self.signature

    def build_post_policy(self, policy):
        return json.dumps(policy)

    def update_post_params(self, params):
        if 'targetpath' in params:
            del params['targetpath']
        if 'targetname' in params:
            del params['targetname']
        self.build_post_data()
        params.update(self.post_data)
