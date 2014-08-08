postgresql: 
    pkg.installed:
        - name: postgresql-9.1
    service.running:
        - name: postgresql
    file.symlink:
        - name: /usr/bin/postgres
        - target: /usr/lib/postgresql/9.1/bin/postgres
    postgres_user.present:
        - name: nextgis
        - user: postgres
    require:
        - file: /etc/hosts
        - pkg: language-pack-en 
    watch:
        - file: /etc/postgresql/9.1/main/pg_hba.conf
        - file: /etc/postgresql/9.1/main/postgresql.conf
        
postgis:
    pkg.installed:
        - name: postgresql-9.1-postgis

locale:
    pkg.installed:
        - name: language-pack-en
    file.managed:
        - source: salt://db-precise/locale
        - name: /etc/default/locale

sudo:
    pkg.installed:
        - name: sudo

/etc/hosts:
    file.managed:
        - source: salt://db-precise/hosts

/etc/postgresql/9.1/main/pg_hba.conf:
    file.managed:
        - source: salt://db-precise/pg_hba.conf

/etc/postgresql/9.1/main/postgresql.conf:
    file.managed:
        - source: salt://db-precise/postgresql.conf


/usr/bin/pg_setup.sh:
    file.managed:
        - source: salt://db-precise/pg_setup.sh
        - mode: 755

/usr/bin/pg_erase.sh:
    file.managed:
        - source: salt://db-precise/pg_erase.sh
        - mode: 755






