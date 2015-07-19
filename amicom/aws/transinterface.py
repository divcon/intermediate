# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import
import json

import boto
from boto import elastictranscoder

from .authentication import AuthentiCation
from .baseinterface import BaseInterface


class TransCoder(BaseInterface):
    def __init__(self):
        self.aws_transcoder = boto.connect_elastictranscoder(AuthentiCation.access_key, AuthentiCation.secret_key,)
        self.aws_transcoder = boto.elastictranscoder.connect_to_region('ap-northeast-1')
        self.pipeline_id = '1437294072599-2bekkw'
        self.presetId = '1351620000001-000020'

    def transcode(self, file_name):
        input_key = self.input_dir + file_name + self.input_extention
        output_key = self.output_dir + file_name + self.output_extention

        job_input = {
            'Key': input_key
        }

        mp4_360p = {
            'Key': output_key,
            'PresetId': self.presetId
        }
        job_outputs = [mp4_360p]

        create_job_result = self.aws_transcoder.create_job(pipeline_id=self.pipeline_id, input_name=job_input,
                                                           output=None, outputs=job_outputs, output_key_prefix=None,
                                                           playlists=None)
        print 'HLS job has been created: ', json.dumps(create_job_result['Job']['Id'], indent=4, sort_keys=True)
