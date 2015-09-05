# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import
import os
from django.utils.datastructures import MultiValueDictKeyError

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


class AlertsPrefix(Singleton):
    __prefix = 0

    def __init__(self):
        super(AlertsPrefix, self).__init__()

    @property
    def prefix(self):
        if self.__prefix > 100:
            self.__prefix = 0
        self.__prefix += 1
        return self.__prefix


def transcoding(origin_filename):
    print "transcoding start"
    s3 = S3Interface()
    filename = origin_filename.split('.')[0]
    print "upload : " + filename
    s3.upload(MEDIA_ROOT, filename)
    print "transcoding ...."
    transcoder = TransCoder()
    transcoder.transcode(filename)
    print "download : " + filename
    s3.download(MEDIA_ROOT, filename)
    print "complete transcoding"


def delete_local_media_file(origin_filename):
    upload_file_path = origin_filename + ".avi"
    download_file_path = origin_filename + ".mp4"
    print "delete local media file : " + upload_file_path + ", " + download_file_path
    if os.path.exists(upload_file_path):
            os.remove(upload_file_path)
    if os.path.exists(download_file_path):
            os.remove(download_file_path)


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
        prefix_num = AlertsPrefix().prefix
        # video_filename = MEDIA_ROOT+'/'+str(prefix_num)+request.FILES['alert[video]'].name
        # file_content = ContentFile(request.FILES['alert[video]'].read())
        # with open(video_filename, "wb") as fp:
        #     for chunk in file_content.chunks():
        #         fp.write(chunk)
        # audio_file_content = ContentFile(request.FILES['alert[audio]'].read())
        # audio_filename = MEDIA_ROOT+'/'+str(prefix_num)+request.FILES['alert[audio]'].name
        # with open(audio_filename, "wb") as fp:
        #     for chunk in audio_file_content.chunks():
        #         fp.write(chunk)
        #
        # audio_convert_file_name = MEDIA_ROOT+'/'+str(prefix_num)+request.FILES['alert[audio]'].name.split('.')[0]+'.wav'
        # encoded_file_name = MEDIA_ROOT+'/'+"new"+str(prefix_num)+request.FILES['alert[video]'].name
        # mp4_file_name = encoded_file_name.split('.')[0]+'.mp4'
        # video_filename_without_path = "new"+str(prefix_num)+request.FILES['alert[video]'].name
        # sox_command = 'sox -t ul -U -r 16000 -c 1 ' + audio_filename + ' ' + audio_convert_file_name
        # avconv_command = 'avconv -i ' + audio_convert_file_name + ' -i ' + video_filename + \
        #                  ' -acodec copy -vcodec copy ' + encoded_file_name
        # print "sox, avconv commands"
        # print sox_command
        # os.system(sox_command)
        # print avconv_command
        # os.system(avconv_command)
        #
        # transcoding(video_filename_without_path)
        filename_list = list()
        mp4_list = list()
        for i in range(1, 5):
            video_param = 'alert[video'+str(i)+']'
            audio_param = 'alert[audio'+str(i)+']'
            mp4, filename = combine_video(video_param, audio_param, prefix_num, request)
            mp4_list.append(mp4)
            filename_list.append(filename)

        result_file_path = base_dir+'/event_result'+filename_list[0]
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
              ' --form "alert[video1]=@' + mp4_list[0] + ';type=video/mp4" ' + \
              ' --form "alert[video2]=@' + mp4_list[1] + ';type=video/mp4" ' + \
              ' --form "alert[video3]=@' + mp4_list[2] + ';type=video/mp4" ' + \
              ' --form "alert[video4]=@' + mp4_list[3] + ';type=video/mp4" ' + \
              'http://104.236.199.54/alerts.json >> ' + result_file_path
        os.system(cmd)
        print "event command : " + cmd
        with open(result_file_path) as result_file:
            data = result_file.readlines()
        if os.path.exists(result_file_path):
            os.remove(result_file_path)

        # delete_local_media_file(video_filename.split('.')[0])
        return HttpResponse(data)


def combine_video(video_param, audio_param, prefix_num, request):
    video_filename = MEDIA_ROOT+'/'+str(prefix_num)+request.FILES[video_param].name
    file_content = ContentFile(request.FILES[video_param].read())
    with open(video_filename, "wb") as fp:
        for chunk in file_content.chunks():
            fp.write(chunk)
    audio_file_content = ContentFile(request.FILES[audio_param].read())
    audio_filename = MEDIA_ROOT+'/'+str(prefix_num)+request.FILES[audio_param].name
    with open(audio_filename, "wb") as fp:
        for chunk in audio_file_content.chunks():
            fp.write(chunk)

    audio_convert_file_name = MEDIA_ROOT+'/'+str(prefix_num)+request.FILES[audio_param].name.split('.')[0]+'.wav'
    encoded_file_name = MEDIA_ROOT+'/'+"new"+str(prefix_num)+request.FILES[video_param].name
    mp4_file_name = encoded_file_name.split('.')[0]+'.mp4'
    video_filename_without_path = str(prefix_num)+request.FILES[video_param].name
    print video_filename_without_path
    # video_filename_without_path = "new"+str(prefix_num)+request.FILES[video_param].name
    # sox_command = 'sox -t ul -U -r 16000 -c 1 ' + audio_filename + ' ' + audio_convert_file_name
    # avconv_command = 'avconv -i ' + audio_convert_file_name + ' -i ' + video_filename + \
    #                  ' -acodec copy -vcodec copy ' + encoded_file_name
    # print "sox, avconv commands"
    # print sox_command
    # os.system(sox_command)
    # print avconv_command
    # os.system(avconv_command)

    transcoding(video_filename_without_path)

    return mp4_file_name, video_filename_without_path


class TrackPrefix(Singleton):
    __prefix = 0

    def __init__(self):
        super(TrackPrefix, self).__init__()

    @property
    def prefix(self):
        if self.__prefix > 100:
            self.__prefix = 0
        self.__prefix += 1
        return self.__prefix


@csrf_exempt
def fleet_track1(request):
    import os
    if request.method == 'POST':
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prefix_num = TrackPrefix().prefix
        rear_img = None
        front_img = None
        try:
            rear_img = MEDIA_ROOT+'/'+str(prefix_num)+request.FILES['track[rear_img]'].name
            rear_file_content = ContentFile(request.FILES['track[rear_img]'].read())
            with open(rear_img, "wb") as fp:
                for chunk in rear_file_content.chunks():
                    fp.write(chunk)
            front_img = MEDIA_ROOT+'/'+str(prefix_num)+request.FILES['track[front_img]'].name
            front_file_content = ContentFile(request.FILES['track[front_img]'].read())
            with open(front_img, "wb") as fp:
                for chunk in front_file_content.chunks():
                    fp.write(chunk)
            image_cmd_string = ' --form "track[rear_img]=@' + rear_img + ';type=image/jpeg" ' + \
                               ' --form "track[front_img]=@' + front_img + ';type=image/jpeg" '
        except MultiValueDictKeyError as e:
            image_cmd_string = ''
        result_file_path = base_dir+'/'+str(prefix_num)+'track1_result'
        print result_file_path

        # --form 'track[front_img]=@$FRONT_JPEG;type=image/jpeg' --form 'track[rear_img]=@$REAR_JPEG;type=image/jpeg'
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
              image_cmd_string + \
              ' http://104.236.199.54/tracks.json >> ' + result_file_path
        os.system(cmd)
        print "track command : " + cmd
        with open(result_file_path) as result_file:
            data = result_file.readlines()
        if os.path.exists(result_file_path):
            os.remove(result_file_path)
        if image_cmd_string != '':
            delete_file(rear_img)
            delete_file(front_img)
        return HttpResponse(data)


def delete_file(origin_filename):
    print "delete local media file : " + origin_filename
    if os.path.exists(origin_filename):
            os.remove(origin_filename)


@csrf_exempt
def test(request):
    video_filename = MEDIA_ROOT+'/'+'121212'+request.FILES['track[video]'].name
    file_content = ContentFile(request.FILES['track[video]'].read())
    with open(video_filename, "wb") as fp:
        for chunk in file_content.chunks():
            fp.write(chunk)
    return HttpResponse()
