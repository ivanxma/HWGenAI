. ./comm.sh
mysql -u$USER -p -h$HOST -P$PORT << EOL
drop database quickstart;

EOL
