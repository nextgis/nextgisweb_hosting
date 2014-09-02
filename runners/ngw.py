
import salt.client
import yaml
import salt.wheel
import time


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


def create(**kwargs):

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

def destroy(**kwargs):

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



