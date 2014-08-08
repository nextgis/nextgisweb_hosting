
import salt.client
import yaml


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

    cli.cmd('master-18', 'cmd.run', ['lxc-genconf.sh {0} {1}'.format(
          kwargs['identifier']
        , kwargs['image'])]) 
    cli.cmd( 'master-18'
           , 'cmd.run'
           , ['ngw-instance-configure.sh {0} {1} {2} {3}'.format( 
                  kwargs['identifier']
                , kwargs['database']
                , kwargs['username']
                , kwargs['password'])]) 
    cli.cmd('db-precise.ngw', 'cmd.run', ['pg_setup.sh {0} {1} {2}'.format(
          kwargs['database']
        , kwargs['username']
        , kwargs['password'])]) 
    cli.cmd('proxy.ngw', 'cmd.run', ['nginx-genconf.sh {0} {1} {2}'.format(
          kwargs['identifier']
        , kwargs['hostname']+'.gis.to'
        , kwargs['identifier']+'.ngw')])

    cli.cmd('master-18', 'cmd.run', ['lxc-start --daemon --name ngw-{0}'.format(kwargs['identifier'])])
    cli.cmd( 'salt.ngw'
           , 'cmd.run'
           , ['salt-run state.event "salt/minion/{0}.ngw/start" count=1 quiet=True'.format(
               kwargs['identifier'])])
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

    # cli.cmd('master-18', 'cp.get_file', ['salt://master-18/tempora /tmp/tempora'])
    # I have no idea why it silently and quickly fails.
    # cli.cmd('master-18', 'cmd.run', ['salt-call cp.get_file salt://master-18/tempora /tmp/tempora'])
    # This works anyway.
    
    cli.cmd('master-18', 'cmd.run', ['salt-call cp.get_template salt://master-18/tempora /tmp/tempora'])
    del cli



