import flask
import jinja2
from os.path import join, dirname, realpath
import psycopg2
import subprocess
import time


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

@app.route('/destroy', methods=['GET'])
def destroy(): 

    conn = psycopg2.connect(database="front", user="front", password="front", host="db-precise")
    cur = conn.cursor()

    try:
        cur.execute( ''' update instances set instanceordered = False where instanceid = %s '''
                , [ flask.request.args['instanceid'] ]
                )

    except psycopg2.Error as e:
        ret = e.pgerror

    else:
        subprocess.call(['logger', '-p', 'local0.notice', '-t', 'NGW-MANAGE'
            , 'Web UI calls destruction: %s.' % flask.request.args['instanceid']])
        subprocess.call(['sudo', 'ngw-manager.sh', 'destroy', flask.request.args['instanceid']])
        ret = 'True'


    finally:
        conn.commit()
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
    ret = ''.join( [ _render('header.jinja2' ) ]
        + [ _render('form_create.jinja2', {'LastEntry': '%03d' % instance_new_id }) ]
        + [ _render('row.jinja2', row) for row in rows ]
        + [ _render('footer.jinja2') ] )

    return ret 

def _db_init():
    conn = psycopg2.connect(database="front", user="front", password="front", host="db-precise")
    cur = conn.cursor()
    cur.execute( ''' create table if not exists "instances"
                ( id serial primary key
                , InstanceID varchar not null unique
                , InstanceClass varchar not null
                , InstanceName varchar not null unique
                , InstanceOrdered boolean
                , InstanceActive boolean
                , InstanceEventAccepted boolean
                ); ''' ) 
    conn.commit()
    cur.close()
    conn.close() 

def _uncheck_event(__id):
    conn = psycopg2.connect(database="front", user="front", password="front", host="db-precise")
    cur = conn.cursor()
    try:
        cur.execute( ''' select instanceeventaccepted
                from instances where instanceid = %s ''' , [__id] ) 
    except psycopg2.Error as e:
        return e.pgerror
    except Exception as e:
        return str(e)
    else:
        if cur.rowcount == 1 and cur.fetchone()[0] == True: 
            try:
                cur.execute(''' update instances
                        set instanceeventaccepted = False where instanceid = %s''' , [__id] )
                conn.commit()
            except psycopg2.Error as e: 
                return e.pgerror
            except Exception as e:
                return str(e)
            return True

    return False 

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
                    , instanceactive )
                    values ( %s , %s , %s , True , False ); '''
                , [ form ['InstanceID'], form ['InstanceClass'], form ['InstanceName'] ]
                ) 
        conn.commit()
    except psycopg2.Error as e:
        return e.pgerror
    except Exception as e:
        return str(e)

    flag = False
    count = 0
    while not flag and count < 13:
        subprocess.call(['logger', '-p', 'local0.notice', '-t', 'NGW-MANAGE'
                , form ['InstanceID'], form ['InstanceClass'], form ['InstanceName']])
        subprocess.call(['sudo', 'ngw-manager.sh', 'create'
                , form ['InstanceID'], form ['InstanceClass'], form ['InstanceName']])
        time.sleep(1)
        count += 1
        flag = _uncheck_event(form['InstanceID'])

    return flask.redirect('http://console.gis.to', code=302)

if __name__ == '__main__':
    # if not app.debug:
    #     import logging
    #     file_handler = logging.FileHandler(filename = '/tmp/flask.log')
    #     app.logger.addHandler (file_handler)
    app.run()

