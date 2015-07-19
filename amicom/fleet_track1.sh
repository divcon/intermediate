
WAIT_FOR_IF_UP=3
PPP_UP=0
COUNTER=0

while [ $COUNTER -lt $WAIT_FOR_IF_UP ]; do

    COUNTER=$((COUNTER + 1))

    if [ -e /etc/fleet/system_start_time ] ; then

                COOKIE=`cat /etc/fleet/cookie`
                #COOKIE=`cat ./cookie`
                SYSTEM_START_TIME=`cat /etc/fleet/system_start_time`
                #CURRENT_TIME=`date "+%F %T"`
                LATITUDE=$1
                LONGITUDE=$2
                STATUS=$3
                SPEEDOVERGROUND=$4
                SPEED_MAX=$5
                SPEED_AVERAGE=$6
                CURRENT_TIME=$7
                TRACK_DISTANCE=$8
                ELAPSED_TIME=$9

                if [ -e /tmp/driver_id.txt ]; then
                        DRIVER_ID=`cat /tmp/driver_id.txt`
                fi

        PPP_UP=1
                curl -H "Cookie: _trackvue_session=$COOKIE" --form "track[driver_id]=$DRIVER_ID" --form "track[start_time]=$SYSTEM_START_TIME GMT+0000" --form "track[end_time]=$CURRENT_TIME GMT+0000" --form "track[speed]=$SPEEDOVERGROUND" --form "track[speed_max]=$SPEED_MAX" --form "track[speed_avg]=$SPEED_AVERAGE" --form "track[status]=$STATUS" --form "track[from_lat]=$LATITUDE" --form "track[from_lng]=$LONGITUDE" --form "track[to_lat]=$LATITUDE" --form "track[to_lng]=$LONGITUDE" --form "track[elapsed]=$ELAPSED_TIME" --form "track[distance]=$TRACK_DISTANCE" --form "track[count_off]=0" --form "track[count_idle]=1" --form "track[count_slow]=0" --form "track[count_normal]=1" --form "track[count_fast]=0" --form "track[count_speeding]=0" http://104.236.199.54/tracks.json > /tmp/curl_result

                curl_result=`cat /tmp/curl_result | grep driver_id | grep -v grep`
                if test -n "$curl_result" ; then
                        if [ ! -e /mnt/mmc/nodingdong.txt ]; then
                                aplay --rate=22050 --channel=1 --format=S16_LE /usr/pcm/cl_dinfdong_22050.wav
                        fi
                fi

                exit 0
   else
       echo -n "."
       sleep 3
    fi
done
