
import salt.client
import yaml
import salt.wheel
import time
import subprocess
import psycopg2
import requests

from functools import wraps
import errno
import os
import signal

class TimeoutError(Exception):
    pass

def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator

def _log(message, tag = "NGW", facility = "local0", priority = "notice"):
    subprocess.call(["logger", "-t", tag, "-p", "%s.%s" % (facility, priority), message])
    print "-p %s.%s" % (facility, priority)
    
def _cmd_run(cli, target, *args):
    for arg in args:
        cli.cmd(target, 'cmd.run', [arg], timeout = 30)
        _log("Command <%s> has run on host <%s>." % (arg, target), priority = 'info') 

@timeout(60)
def _sleep_on_event(event, tag, target, keys = {}, wait = 60, timeout = 300):
    _log("Sleeping on event with tag <%s> from host <%s>." % (tag, target))
    time_limit = time.time()
    unmatched = False
    while True:
        value = event.get_event(wait = wait, tag = tag, use_pending = True)
        if value and value['id'] == target:
            for key in keys:
                if not value[key] or value[key] != keys[key]:
                    unmatched = True
                    break

            if time.time() > time_limit:
                _log("Wait for event with tag <%s> from host <%s> timed out." % (tag, target))
                return False
            elif unmatched:
                continue
            else:
                _log("Event with tag <%s> caught from host <%s> and matched." % (tag, target))
                return True

def create(**kwargs): 
    cli = salt.client.LocalClient(__opts__['conf_file'])
    wheel = salt.wheel.Wheel(salt.config.master_config('/etc/salt/master'))
    event = salt.utils.event.MasterEvent('/var/run/salt/master')

    # _cmd_run(cli, 'master-18', 'touch /tmp/touch.me', 'touch /tmp/touch_2.me')
    # yaml.dump(cli.cmd('salt.ngw', 'state.highstate'), file('/tmp/salt.yaml', 'w'))

    # ret = cli.cmd('salt.ngw', 'state.highstate')
    # for target in ret:
    #     for key in data if key == "result" and data["key"]:
    #         file('/tmp/salt.log', 'w')).write("

    __id = kwargs ['id']
    __class = kwargs ['class']
    __name = kwargs ['name']
    int_name = str(__id) + '.ngw'
    ext_name = str(__name) + '.gis.to'

    _log("Create event caught, id: <%s>, class: <%s>, name: <%s>." % (__id, __class, __name)
            , tag = "NGW-MANAGE") 

    conn = psycopg2.connect(database="front", user="front", password="front", host="db-precise")
    cur = conn.cursor()
    cur.execute( ''' update instances
            set instanceeventaccepted = True where instanceid = %s ''' , [__id]) 
    conn.commit()
    if cur.rowcount == 1:
        _log("An instance <%s> tagged as accepted." % __id)
    else:
        _log('Something strange happened: %s instances ' \
        'were tagged as accepted while trying %s.' % (cur.rowcount, __id))

    cur.execute( ''' select instanceactive from instances '''
            ''' where instanceid = %s and instanceactive = True ''', [__id])
    if cur.rowcount == 1:
        _log("An instance <%s> already marked as active. Interrupt." % __id)
        return False


    _cmd_run(cli, 'master-18', 'lxc-genconf.sh %s %s' % (__id, __class))
    _cmd_run(cli, 'master-18', 'ngw-instance-configure.sh %s %s %s %s' % ((__id,) * 4))
    _cmd_run(cli, 'db-precise.ngw', 'pg_setup.sh %s %s %s' % ((__id,) * 3))
    _cmd_run(cli, 'proxy.ngw', 'nginx-genconf.sh %s %s %s' % (__id, ext_name, int_name))
    _cmd_run(cli, 'master-18', 'lxc-start --daemon --name ngw-%s' % __id) 
    _sleep_on_event(event, tag = 'salt/auth', target = int_name, keys = {'act': 'pend'}) 
    wheel.call_func('key.accept', match = int_name) 
    _sleep_on_event(event, tag = 'salt/minion/%s/start' % int_name, target = int_name)
    cli.cmd(int_name, 'state.highstate')
    _cmd_run(cli, int_name, 'initctl stop ngw-uwsgi')
    _cmd_run(cli, int_name, '~ngw/env/bin/nextgisweb --config ~ngw/config.ini initialize_db') 
    _cmd_run(cli, int_name, 'initctl start ngw-uwsgi')
    _cmd_run(cli, 'proxy.ngw', 'service nginx reload')

    _log("Create event finished, id: <%s>, class: <%s>, name: <%s>." % (__id, __class, __name)
            , tag = "NGW-MANAGE") 
    response = requests.get("http://proxy/activate?instanceid=%s" % __id
            , headers = { 'host': 'console.gis.to'})

    if response.content == "True":
        _log("Instance <%s> activated." % __id)
    else:
        _log("Failed to activate instance <%s>." % __id)


    del cli

def destroy(**kwargs):
    cli = salt.client.LocalClient(__opts__['conf_file'])
    wheel = salt.wheel.Wheel(salt.config.master_config('/etc/salt/master'))
    event = salt.utils.event.MasterEvent('/var/run/salt/master')

    __id = kwargs ['id']
    int_name = __id + '.ngw'

    _log("Destroy event caught, id: <%s>." % (__id)
            , tag = "NGW-MANAGE")

    conn = psycopg2.connect(database="front", user="front", password="front", host="db-precise")
    cur = conn.cursor()
    cur.execute( ''' update instances
            set instanceeventaccepted = True where instanceid = %s ''' , [__id]) 
    conn.commit()
    if cur.rowcount == 1:
        _log("An instance <%s> tagged as accepted." % __id)
    else:
        _log('Something strange happened: %s instances ' \
        'were tagged as accepted while trying %s.' % (cur.rowcount, __id)) 

    _cmd_run(cli, 'proxy.ngw', 'nginx-rmconf.sh %s' % __id)
    _cmd_run(cli, 'proxy.ngw', 'service nginx reload')
    _cmd_run(cli, 'master-18', 'lxc-rmconf.sh %s' % __id)
    _cmd_run(cli, 'db-precise.ngw', 'pg_erase.sh %s %s' % ((__id,)*2))
    wheel.call_func('key.delete', match = int_name)

    conn.close()


    del cli 
    del wheel
    del event

    _log("Destroy event finished, id: <%s>." % (__id)
            , tag = "NGW-MANAGE")


    return True


def dummy():
    pass


def _check_event(__id):
    pass

#

    # def destroy(**kwargs):
    #     cli = salt.client.LocalClient(__opts__['conf_file'])
    #     wheel = salt.wheel.Wheel(salt.config.master_config('/etc/salt/master'))
    #     event = salt.utils.event.MasterEvent('/var/run/salt/master')
    # 
    #     __id = kwargs ['id']
    #     int_name = __id + '.ngw'
    # 
    #     _log("Destroy event caught, id: <%s>." % (__id)
    #             , tag = "NGW-MANAGE")
    # 
    #     _cmd_run(cli, 'proxy.ngw', 'nginx-rmconf.sh %s' % __id)
    #     _cmd_run(cli, 'proxy.ngw', 'service nginx reload')
    #     _cmd_run(cli, 'master-18', 'lxc-rmconf.sh %s' % __id)
    #     _cmd_run(cli, 'db-precise.ngw', 'pg_erase.sh %s %s' % ((__id,)*2))
    #     wheel.call_func('key.delete', match = int_name)
    # 
    #     _log("Destroy event finished, id: <%s>." % (__id)
    #             , tag = "NGW-MANAGE")
    # 
    #     del cli 

