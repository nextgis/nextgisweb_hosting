pg_database="$1"
pg_username="$2"

cd /tmp
sudo -u postgres psql -c "drop database \"$pg_database\" ;" > /dev/null
sudo -u postgres psql -c "drop user \"$pg_username\" " > /dev/null

