# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import boto
import time

from .authentication import AuthentiCation
from .baseinterface import BaseInterface


class S3Interface(BaseInterface):
    def __init__(self):
        self.aws_s3 = boto.connect_s3(AuthentiCation.access_key, AuthentiCation.secret_key)
        self.bucket = self.aws_s3.get_bucket(self.bucket_name)

    def upload(self, src_dir, file_name):
        src = src_dir + file_name + self.input_extention
        fp = open(src, 'rb')
        key = self.bucket.new_key(self.input_dir+file_name+self.input_extention)
        key.set_contents_from_file(fp)

    def download(self, des_dir, file_name):
        key = self.bucket.get_key(self.output_dir+file_name+self.output_extention)
        key.get_contents_to_filename(des_dir+file_name+self.output_extention)
