# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import
import os

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.files.base import ContentFile
from amicom.settings import MEDIA_ROOT

from aws.s3interface import S3Interface
from aws.transinterface import TransCoder


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance


class Postfix(Singleton):
    __postfix = 0

    def __init__(self):
        super(Postfix, self).__init__()

    @property
    def postfix(self):
        if self.__postfix > 100:
            self.__postfix = 0
        self.__postfix += 1
        return self.__postfix


def transcoding(origin_filename):
    print "transcoding start"
    s3 = S3Interface()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filename = origin_filename.split('.')[0]
    print "upload : " + filename
    s3.upload(MEDIA_ROOT, filename)
    print "transcoding ...."
    transcoder = TransCoder()
    transcoder.transcode(filename)
    print "download : " + filename
    s3.download(MEDIA_ROOT, filename)
    print "complete transcoding"


@csrf_exempt
def signin(request):
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result_file_path = base_dir+'/signin_result'
    apiURL = 'http://104.236.199.54/signin'
    cmd = "curl -c " + result_file_path + " -d 'user[email]=" + request.POST['user[email]'] + \
          "' -d 'user[password]="+request.POST['user[password]']+"' http://104.236.199.54/signin"
    os.system(cmd)
    result_file = open(result_file_path)
    data = result_file.readlines()
    result_file.close()
    os.system("rm -rf "+result_file_path)
    return HttpResponse(data)


@csrf_exempt
def fleet_event(request):
    import os
    if request.method == 'POST':
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        postfix_num = Postfix().postfix
        video_filename = MEDIA_ROOT+'/'+str(postfix_num)+request.FILES['alert[video]'].name
        file_content = ContentFile(request.FILES['alert[video]'].read())
        with open(video_filename, "wb") as fp:
            for chunk in file_content.chunks():
                fp.write(chunk)
        mp4_file_name = video_filename.split('.')[0]+'.mp4'
        video_filename_without_path = str(postfix_num)+request.FILES['alert[video]'].name
        transcoding(video_filename_without_path)

        result_file_path = base_dir+'/event_result'+video_filename_without_path
        print result_file_path
        os.system("rm -rf "+result_file_path)
        cmd = 'curl -v -H "Cookie: _trackvue_session=' + request.POST['cookie'] + '"' + \
              ' --form "alert[driver_id]=' + request.POST['alert[driver_id]'] + '"' + \
              ' --form "alert[trip_start_time]=' + request.POST['alert[trip_start_time]'] + '"' + \
              ' --form "alert[alert_time]=' + request.POST['alert[alert_time]'] + '"' + \
              ' --form "alert[alert_type]=' + request.POST['alert[alert_type]'] + '"' + \
              ' --form "alert[severity]=' + request.POST['alert[severity]'] + '"' + \
              ' --form "alert[value]=' + request.POST['alert[value]'] + '"' + \
              ' --form "alert[lat]=' + request.POST['alert[lat]'] + '"' + \
              ' --form "alert[lng]=' + request.POST['alert[lng]'] + '"' + \
              ' --form "alert[video]=@' + mp4_file_name + ';type=video/mp4" ' + \
              'http://104.236.199.54/alerts.json >> ' + result_file_path
        os.system(cmd)
        print "event command : " + cmd
        result_file = open(result_file_path)
        data = result_file.readlines()
        result_file.close()
        os.system("rm -rf "+result_file_path)
        return HttpResponse(data)


@csrf_exempt
def fleet_track1(request):
    import os
    if request.method == 'POST':
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result_file_path = base_dir+'/track1_result'+request.POST['track[driver_id]']+request.POST['track[end_time]']
        print result_file_path
        cmd = 'curl -H "Cookie: _trackvue_session=' + request.POST['cookie'] + '"' + \
              ' --form "track[driver_id]=' + request.POST['track[driver_id]'] + '"' + \
              ' --form "track[start_time]=' + request.POST['track[start_time]'] + '"' + \
              ' --form "track[end_time]=' + request.POST['track[end_time]'] + '"' + \
              ' --form "track[speed]=' + request.POST['track[speed]'] + '"' + \
              ' --form "track[speed_max]=' + request.POST['track[speed_max]'] + '"' + \
              ' --form "track[speed_avg]=' + request.POST['track[speed_avg]'] + '"' + \
              ' --form "track[status]=' + request.POST['track[status]'] + '"' + \
              ' --form "track[from_lat]=' + request.POST['track[from_lat]'] + '"' + \
              ' --form "track[from_lng]=' + request.POST['track[from_lng]'] + '"' + \
              ' --form "track[to_lat]=' + request.POST['track[to_lat]'] + '"' + \
              ' --form "track[to_lng]=' + request.POST['track[to_lng]'] + '"' + \
              ' --form "track[elapsed]=' + request.POST['track[elapsed]'] + '"' + \
              ' --form "track[distance]=' + request.POST['track[distance]'] + '"' + \
              ' --form "track[count_off]=' + request.POST['track[count_off]'] + '"' + \
              ' --form "track[count_idle]=' + request.POST['track[count_idle]'] + '"' + \
              ' --form "track[count_slow]=' + request.POST['track[count_slow]'] + '"' + \
              ' --form "track[count_normal]=' + request.POST['track[count_normal]'] + '"' + \
              ' --form "track[count_fast]=' + request.POST['track[count_fast]'] + '"' + \
              ' --form "track[count_speeding]=' + request.POST['track[count_speeding]'] + '"' + \
              ' http://104.236.199.54/tracks.json >> ' + result_file_path
        os.system(cmd)
        print "track command : " + cmd
        result_file = open(result_file_path)
        data = result_file.readlines()
        result_file.close()
        os.system("rm -rf "+result_file_path)
        return HttpResponse(data)


@csrf_exempt
def test(request):
    video_filename = MEDIA_ROOT+'/'+'121212'+request.FILES['track[video]'].name
    file_content = ContentFile(request.FILES['track[video]'].read())
    with open(video_filename, "wb") as fp:
        for chunk in file_content.chunks():
            fp.write(chunk)
    return HttpResponse()
