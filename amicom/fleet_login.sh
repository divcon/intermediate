
#START_DATE_TIME=`date "+%F %T"`
#echo $START_DATE_TIME > /etc/fleet/system_start_time

# rm -f /etc/fleet/cookiefile
# rm -f /etc/fleet/cookie

# curl -c /etc/fleet/cookiefile -d 'user[email]=test@trackvue.com' -d 'user[password]=admin123' http://104.236.199.54/signin
curl -c /etc/fleet/cookiefile -d 'user[email]=test@trackvue.com' -d 'user[password]=admin123' http://104.236.199.54/signin

# Extract encoded part for HTTP Cookie Header from the cookiefile

# cat /etc/fleet/cookiefile | grep -v ^'# '| grep -v ^$| grep -v POST$|cut -f7 > /etc/fleet/cookie

DRIVER_ID=9
echo $DRIVER_ID > /tmp/driver_id.txt
