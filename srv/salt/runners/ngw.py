
import salt.client
import yaml
import salt.wheel
import time
import subprocess


def up():
    '''
    Print a list of all of the minions that are up
    '''
    client = salt.client.LocalClient(__opts__['conf_file'])
    minions = client.cmd('*', 'test.ping', timeout=1)
    for minion in sorted(minions):
        print minion
    del client


def r1(*args,**kwargs):
    cli = salt.client.LocalClient()

    


    del cli

def _log(message, tag = "NGW", facility = "local0", priority = "notice"):
    subprocess.call(["logger", "-t", tag, "-p", "%s.%s" % (facility, priority), message])
    print "-p %s.%s" % (facility, priority)
    

def _cmd_run(cli, target, *args):
    for arg in args:
        cli.cmd(target, 'cmd.run', [arg], timeout = 30)
        _log("Command <%s> has run on host <%s>." % (arg, target), priority = 'info') 

        # yaml.dump(output, (file('/tmp/salt.yaml', 'w')), default_flow_style=False)

def _sleep_on_event(event, tag, target, keys = {}, wait = 60, timeout = 300):
    _log("Sleeping on event with tag <%s> from host <%s>." % (tag, target))
    time_limit = time.time() + timeout
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
    int_name = __id + '.ngw'
    ext_name = __name + '.gis.to'

    _log("Create event caught, id: <%s>, class: <%s>, name: <%s>." % (__id, __class, __name)
            , tag = "NGW-MANAGE") 

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

    del cli

def destroy(**kwargs):
    cli = salt.client.LocalClient(__opts__['conf_file'])
    wheel = salt.wheel.Wheel(salt.config.master_config('/etc/salt/master'))
    event = salt.utils.event.MasterEvent('/var/run/salt/master')

    __id = kwargs ['id']
    int_name = __id + '.ngw'

    _log("Destroy event caught, id: <%s>." % (__id)
            , tag = "NGW-MANAGE")

    _cmd_run(cli, 'proxy.ngw', 'nginx-rmconf.sh %s' % __id)
    _cmd_run(cli, 'proxy.ngw', 'service nginx reload')
    _cmd_run(cli, 'master-18', 'lxc-rmconf.sh %s' % __id)
    _cmd_run(cli, 'db-precise.ngw', 'pg_erase.sh %s %s' % ((__id,)*2))
    wheel.call_func('key.delete', match = int_name)

    _log("Destroy event finished, id: <%s>." % (__id)
            , tag = "NGW-MANAGE")

    del cli 

def create_obsolete_summer(**kwargs):

    cli = salt.client.LocalClient(__opts__['conf_file'])
    wheel = salt.wheel.Wheel(salt.config.master_config('/etc/salt/master'))
    event = salt.utils.event.MasterEvent('/var/run/salt/master')

    open('/tmp/log.out','a').write("Event: /create/ received @ salt. Name {0}".format(kwargs['identifier']))

    cli.cmd('master-18', 'cmd.run', ['lxc-genconf.sh {0} {1}'.format(
          kwargs['identifier']
        , kwargs['image'])]) 
    cli.cmd('db-precise.ngw', 'cmd.run', ['pg_setup.sh {0} {1} {2}'.format(
          kwargs['database']
        , kwargs['username']
        , kwargs['password'])]) 
    cli.cmd( 'master-18'
           , 'cmd.run'
           , ['ngw-instance-configure.sh {0} {1} {2} {3}'.format( 
                  kwargs['identifier']
                , kwargs['database']
                , kwargs['username']
                , kwargs['password'])]) 
    cli.cmd('proxy.ngw', 'cmd.run', ['nginx-genconf.sh {0} {1} {2}'.format(
          kwargs['identifier']
        , kwargs['hostname']+'.gis.to' # External FQDN logic.
        , kwargs['identifier']+'.ngw')]) # Internal FQDN logic.

    cli.cmd('master-18', 'cmd.run', ['lxc-start --daemon --name ngw-{0}'.format(kwargs['identifier'])])

    # cli.cmd( 'salt.ngw'
    #        , 'cmd.run'
    #        , ['salt-run state.event "salt/minion/{0}.ngw/start" count=1 quiet=True'.format(
    #            kwargs['identifier'])])
    # # Obsolete?

    while True:
        event_value = event.get_event(wait=0, tag='salt/auth', use_pending=True)
        if event_value:
            if event_value['id'] == '{0}.ngw'.format(kwargs['identifier']) and event_value['act']=='pend':
                break

    wheel.call_func('key.accept', match='{0}.ngw'.format(kwargs['identifier']))

    while True:
        event_value = event.get_event(wait=0, tag='salt/minion/{0}.ngw/start'.format(kwargs['identifier']))
        if event_value:
            break

    cli.cmd(kwargs['identifier'] + '.ngw', 'cmd.run', ['initctl stop ngw-uwsgi'])
    cli.cmd(kwargs['identifier'] + '.ngw', 'cmd.run', ['~ngw/env/bin/nextgisweb --config ~ngw/config.ini initialize_db'])
    cli.cmd(kwargs['identifier'] + '.ngw', 'cmd.run', ['initctl start ngw-uwsgi'])
    cli.cmd('proxy.ngw', 'cmd.run', ['service nginx reload'])

    del cli

def destroy_obsolete_summer(**kwargs):

    cli = salt.client.LocalClient(__opts__['conf_file']) 

    cli.cmd('proxy.ngw', 'cmd.run', ['nginx-rmconf.sh {0}'.format(
          kwargs['identifier'])])
    cli.cmd('proxy.ngw', 'cmd.run', ['service nginx reload'])

    cli.cmd('master-18', 'cmd.run', ['lxc-rmconf.sh {0}'.format(
          kwargs['identifier'])])
    cli.cmd('db-precise.ngw', 'cmd.run', ['pg_erase.sh {0} {1}'.format(
          kwargs['database']
        , kwargs['username'])])


    del cli


def tempora(**kwargs):

    cli = salt.client.LocalClient(__opts__['conf_file'])
    wheel = salt.wheel.Wheel(salt.config.master_config('/etc/salt/master'))
    event = salt.utils.event.MasterEvent('/var/run/salt/master')

    # cli.cmd('master-18', 'cp.get_file', ['salt://master-18/tempora /tmp/tempora'])
    # I have no idea why it silently and quickly fails.
    # cli.cmd('master-18', 'cmd.run', ['salt-call cp.get_file salt://master-18/tempora /tmp/tempora'])
    # This works anyway.
    
    # cli.cmd('master-18', 'cmd.run', ['salt-call cp.get_template salt://master-18/tempora /tmp/tempora'])
    # wheel.call_func('key.accept', match='tempora-10.ngw')
    # cli.cmd('tempora-7' + '.ngw', 'cmd.run', ['user=ngw', 'cwd=/tmp', 'touch ngw-X1'])

    print(event.get_event(wait=0, tag='salt/auth', use_pending=True))

    del cli
    del wheel
    del event



