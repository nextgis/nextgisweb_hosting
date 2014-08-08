pg_database="$1"
pg_user_name="$2"
pg_user_password="$3"

cd /tmp
sudo -u postgres psql -c "create database $pg_database;" > /dev/null
sudo -u postgres psql \
    -c "create role \"$pg_user_name\" login password '$pg_user_password'; " \
    > /dev/null
sudo -u postgres psql \
    -d $pg_database \
    -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql \
    > /dev/null
sudo -u postgres psql -d $pg_database -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql > /dev/null
sudo -u postgres psql -d $pg_database -c "
alter table geometry_columns owner to $pg_user_name;
alter table geography_columns owner to $pg_user_name;
alter table spatial_ref_sys owner to $pg_user_name;
grant all on database $pg_database to $pg_user_name; "
