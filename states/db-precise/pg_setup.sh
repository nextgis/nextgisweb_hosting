pg_database="$1"
pg_username="$2"
pg_password="$3"

cd /tmp
sudo -u postgres psql -c "create database \"$pg_database\" ; " > /dev/null
sudo -u postgres psql \
    -c "create role \"$pg_username\" login password '$pg_password'; " \
    > /dev/null
sudo -u postgres psql -c "grant all on database \"$pg_database\" to \"$pg_username\" ; "

sudo -u postgres psql \
    -d "$pg_database" \
    -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql \
    > /dev/null
sudo -u postgres psql -d "$pg_database" -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql > /dev/null
sudo -u postgres psql -d "$pg_database" -c "
alter table geometry_columns owner to \"$pg_username\";
alter table geography_columns owner to \"$pg_username\";
alter table spatial_ref_sys owner to \"$pg_username\"; "
