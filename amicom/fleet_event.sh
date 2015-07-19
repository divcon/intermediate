</etc/fleet/fleet_event>
COOKIE=`cat /etc/fleet/cookie`
#COOKIE=`cat ./cookie`
SYSTEM_START_TIME=`cat /etc/fleet/system_start_time`
EVENT_TIME=$1
EVENT_TYPE=$2
LATITUDE=$3
LONGITUDE=$4
FRONT_JPEG=$5
REAR_JPEG=$6

# VIDEO_CLIP=$7

TMP_VIDEO_CLIP=`ls /media/mmcblk0p1/backup/ | grep ch0.avi | grep -v grep`
VIDEO_CLIP=/media/mmcblk0p1/backup/$TMP_VIDEO_CLIP
echo "File name : $VIDEO_CLIP"

if [ -e /tmp/driver_id.txt ]; then
        DRIVER_ID=`cat /tmp/driver_id.txt`
fi

curl -v -H "Cookie: _trackvue_session=$COOKIE" --form "alert[driver_id]=$DRIVER_ID" --form "alert[trip_start_time]=$SYSTEM_START_TIME GMT+0000" --form "alert[alert_time]=$EVENT_TIME GMT+0000" --form "alert[alert_type]=$3" --form "alert[severity]=S" --form "alert[value]=109" --form "alert[lat]=$LATITUDE" --form "alert[lng]=$LONGITUDE" --form "alert[video]=@$VIDEO_CLIP;type=video/avi" http://104.236.199.54/alerts.json > /tmp/curl_result
#curl -v -H "Cookie: _trackvue_session=$COOKIE" --form "alert[driver_id]=$DRIVER_ID" --form "alert[trip_start_time]=$SYSTEM_START_TIME GMT+0000" --form "alert[alert_time]=$EVENT_TIME GMT+0000" --form "alert[alert_type]=$3" --form "alert[severity]=S" --form "alert[value]=109" --form "alert[lat]=$LATITUDE" --form "alert[lng]=$LONGITUDE" --form "alert[front_img]=@$FRONT_JPEG;type=image/jpeg"  --form "alert[rear_img]=@$REAR_JPEG;type=image/jpeg" --form "alert[video]=@$VIDEO_CLIP;type=video/avi" http://104.236.199.54/alerts.json > /tmp/curl_result

curl_result=`cat /tmp/curl_result | grep driver_id | grep -v grep`
if test -n "$curl_result" ; then
        if [ ! -e /mnt/mmc/nodingdong.txt ]; then
                aplay --rate=22050 --channel=1 --format=S16_LE /usr/pcm/cl_dinfdong_22050.wav
        fi
else
        echo $1 $2 $3 $4 $5 $6 $TMP_VIDEO_CLIP >> /tmp/event_upload
fi

exit 0
