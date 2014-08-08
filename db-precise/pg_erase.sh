pg_database="$1"
pg_user_name="$2"

cd /tmp
sudo -u postgres psql -c "drop database $pg_database;" > /dev/null
sudo -u postgres psql -c "drop user \"$pg_user_name\" " > /dev/null

