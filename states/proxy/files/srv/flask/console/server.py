import flask
import jinja2
from os.path import join, dirname, realpath
import psycopg2
import subprocess
import time
import redis
import json


app = flask.Flask(__name__)

def _render(template, env = {}):
    return jinja2.Template(open(join(dirname(realpath(__file__)),template)).read()).render(env)

@app.route('/exercise')
def exercise():
    return 'lalafa'

@app.route('/activate', methods=['GET'])
def activate(): 

    conn = psycopg2.connect(database="front", user="front", password="front", host="db-precise")
    cur = conn.cursor()

    try:
        cur.execute( ''' update instances set instanceactive = True where instanceid = %s '''
                , [ flask.request.args['instanceid'] ]
                )

    except psycopg2.Error as e:
        ret = e.pgerror
    except Exception as f:
        return str(f)

    else:
        ret = 'True'

    finally:
        conn.commit()
        cur.close()
        conn.close() 
        return ret 

@app.route('/create', methods = ['POST', 'GET'])
def create():
    form = dict(zip( flask.request.form.keys()
        , [ str(value) for value in flask.request.form.values() ] ) )

    _db_init()

    conn = psycopg2.connect(database="front", user="front", password="front", host="db-precise")
    cur = conn.cursor()

    try:
        cur.execute( ''' insert into instances
                    ( instanceid , instanceclass , instancename , instanceordered
                    , instanceactive , instanceeventaccepted )
                    values ( %s , %s , %s , True , False, False ); '''
                , [ form ['InstanceID'], form ['InstanceClass'], form ['InstanceName'] ]
                ) 
        conn.commit()
    except psycopg2.Error as e:
        return e.pgerror
    except Exception as e:
        return str(e)

    subprocess.call(['logger', '-p', 'local0.notice', '-t', 'NGW-MANAGE'
            , form ['InstanceID'], form ['InstanceClass'], form ['InstanceName']])
    subprocess.call(['sudo', 'ngw-manager.sh', 'create'
            , form ['InstanceID'], form ['InstanceClass'], form ['InstanceName']])

    return flask.redirect('http://console.gis.to', code=302)

@app.route('/restart', methods=['GET'])
def restart():


    subprocess.call(['logger', '-p', 'local0.notice', '-t', 'NGW-MANAGE'
        , 'Web UI calls restart: %s.' % flask.request.args['instanceid']])
    subprocess.call(['sudo', 'ngw-manager.sh', 'restart', flask.request.args['instanceid']])
    ret = 'True'

    return ret 

@app.route('/backup', methods=['GET'])
def backup():
    subprocess.call(['logger', '-p', 'local0.notice', '-t', 'NGW-MANAGE'
        , 'Web UI calls backup: %s.' % flask.request.args['instanceid']])
    subprocess.call(['sudo', 'ngw-manager.sh', 'backup', flask.request.args['instanceid']])
    ret = 'True'

    return ret 

@app.route('/destroy', methods=['GET'])
def destroy(): 

    conn = psycopg2.connect(database="front", user="front", password="front", host="db-precise")
    cur = conn.cursor()

    try:
        cur.execute( ''' update instances set instanceordered = False where instanceid = %s '''
                , [ flask.request.args['instanceid'] ]
                )
        conn.commit()

    except psycopg2.Error as e:
        ret = e.pgerror

    subprocess.call(['logger', '-p', 'local0.notice', '-t', 'NGW-MANAGE'
        , 'Web UI calls destruction: %s.' % flask.request.args['instanceid']])
    subprocess.call(['sudo', 'ngw-manager.sh', 'destroy', flask.request.args['instanceid']])
    ret = 'True'

    try:
        # cur.execute( ''' delete from instances where instanceid = %s '''
        #         , [ flask.request.args['instanceid'] ]
        #         )
        cur.execute( ''' update instances set instanceactive = False where instanceid = %s '''
                , [ flask.request.args['instanceid'] ]
                )
        conn.commit()

    except psycopg2.Error as e:
        ret = e.pgerror

    cur.close()
    conn.close()

    return ret

@app.route('/deactivate', methods=['GET'])
def deactivate(): 

    conn = psycopg2.connect(database="front", user="front", password="front", host="db-precise")
    cur = conn.cursor()

    try:
        cur.execute( ''' update instances set instanceactive = False where instanceid = %s '''
                , [ flask.request.args['instanceid'] ]
                )

    except psycopg2.Error as e:
        ret = e.pgerror
    else:
        ret = 'True'

    finally:
        conn.commit()
        cur.close()
        conn.close() 
        return ret 

@app.route('/')
def index(): 
    _db_init() 
    conn = psycopg2.connect(database="front", user="front", password="front", host="db-precise")
    cur = conn.cursor()

    try:
        cur.execute(''' select instanceid , instanceclass , instancename , instanceordered
                        , instanceactive, instanceeventaccepted
                    from instances where instanceactive = True or instanceordered = True
                    order by id desc ''')
    except psycopg2.Error as e:
        return e.pgerror
    except Exception as e:
        return str(e)

    instance_list_active = cur.fetchall()

    try:
        cur.execute(''' select id from instances
                    order by id desc limit 1''')
    except psycopg2.Error as e:
        return e.pgerror
    except Exception as e:
        return str(e)

    fetch_last = cur.fetchone() # Returns a singleton-tuple or a None value.  

    if fetch_last:
        instance_new_id = fetch_last[0] + 1
    else:
        instance_new_id = 1

    rows = [ { 'InstanceID': fetch_row[0], 'InstanceClass': fetch_row[1]
        , 'InstanceName': fetch_row[2] , 'InstanceOrdered': fetch_row[3]
        , 'InstanceActive': fetch_row[4]}
            for fetch_row in instance_list_active ]
    ret = ''.join \
            ( [ _render('header.jinja2' ) ]
            + [ _render('form_create.jinja2'
                , {
                      'LastEntry': '%03d' % instance_new_id
                    , 'sheep_total': instance_new_id - 1
                    , 'sheep_ordered': len( [row for row in rows if row['InstanceOrdered']])
                    , 'sheep_running': len(
                        [row for row in rows
                            if row['InstanceActive'] and row['InstanceOrdered']])
                    , 'names_running': len(set(
                        [row['InstanceName'] for row in rows
                            if row['InstanceActive'] and row['InstanceOrdered']]))
                    , 'names_total': len(set(
                        [row['InstanceName'] for row in rows ]))
                    }
                )
              ]
            + [ _render('row.jinja2', row) for row in rows ]
            + [ _render('footer.jinja2') ]
            )

    return ret 

@app.route('/backups/<id_>')
def backups(id_):

    r = redis.StrictRedis (host = 'redis.ngw')

    try:
        return ''.join (
              [ _render('backups-header.jinja') ]
              + [ _render('backups-row.jinja', {'InstanceID': id_, 'key': key, 'backups': r.lrange(key, 0, -1)}) for key in r.keys('backups:*') ]
            + [ _render('backups-footer.jinja') ]
            )
    except Exception as e:
        return str(e)


@app.route('/restore', methods=['GET'])
def restore():
    subprocess.call(['logger', '-p', 'local0.notice', '-t', 'NGW-MANAGE'
        , 'Web UI calls restore: {} on {}.' .format (
              flask.request.args['backup']
            , flask.request.args['instanceid']) ]
        )
    subprocess.call(['sudo', 'ngw-manager.sh'
        , 'restore'
        , flask.request.args['backup']
        , flask.request.args['instanceid']])
    ret = 'True'

    return ret 



def _db_init():
    conn = psycopg2.connect(database="front", user="front", password="front", host="db-precise")
    cur = conn.cursor()
    cur.execute( ''' create table if not exists "instances"
                ( id serial primary key
                , InstanceID varchar not null unique
                , InstanceClass varchar not null
                , InstanceName varchar not null
                , InstanceOrdered boolean
                , InstanceActive boolean
                , InstanceEventAccepted boolean
                ); ''' ) 
    conn.commit()
    cur.close()
    conn.close() 

# def _uncheck_event(__id):
#     conn = psycopg2.connect(database="front", user="front", password="front", host="db-precise")
#     cur = conn.cursor()
#     try:
#         cur.execute( ''' select instanceeventaccepted
#                 from instances where instanceid = %s ''' , [__id] ) 
#     except psycopg2.Error as e:
#         return e.pgerror
#     except Exception as e:
#         return str(e)
#     else:
#         if cur.rowcount == 1 and cur.fetchone()[0] == True: 
#             try:
#                 cur.execute(''' update instances
#                         set instanceeventaccepted = False where instanceid = %s''' , [__id] )
#                 conn.commit()
#             except psycopg2.Error as e: 
#                 return e.pgerror
#             except Exception as e:
#                 return str(e)
#             return True
# 
#     return False 

if __name__ == '__main__':
    if not app.debug:
        import logging
        file_handler = logging.FileHandler(filename = '/var/log/flask.log')
        app.logger.addHandler (file_handler)
    app.run()

