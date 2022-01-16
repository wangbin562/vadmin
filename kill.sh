for i in `ps -ef|grep manage.py|grep -v grep|awk '{print $2}'`
do
kill -9 $i
done
