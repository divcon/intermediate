# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import


class BaseInterface(object):
    input_extention = '.avi'
    output_extention = '.mp4'
    input_dir = 'original/'
    output_dir = 'transcode/'
    bucket_name = 'ezeztranstest'
