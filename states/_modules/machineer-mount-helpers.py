import glob
import os
import collections
import re

import dbus

import salt.utils


def echo(*args, **kws):
    return { 'args': args, 'kws': kws }

def status (*args, **kws):
    global opt
    opt = { 'upstart_service_name': 'machineer-mount'
          , 'upstart_service_separator': '( on | with )'
          , 'conf': '/etc/machineer'
          }

    opt = _tree_merge ([opt, kws])

    ret = {}

    ret['src exists'] = True if sum ([
              __salt__['file.is_blkdev']        ( kws['src'])
            , __salt__['file.directory_exists'] ( kws['src'])
            ]) else False
    ret['tgt exists'] = True if __salt__['file.directory_exists'] (kws['tgt']) else False
    ret['exists'] = True if ret['src exists'] and ret['tgt exists'] else False

    ret['running'] = True if len ([ obj for obj in _initctl_machineer_mounts()
            if  { 'name': { key: _initctl_split_name(obj) [key] for key in ['src', 'tgt'] }
                , 'state': obj['state']
                } == { 'name': { k: opt[k] for k in ['src', 'tgt'] }, 'state': 'running' }
            ]) else False

    ret ['enabled'] = True if len ( reduce ( lambda x, y: x + y, [
            [ True for line
            in open (path, 'r') .read() .splitlines()
            if line.split() == {k: opt[k] for k in ['src', 'tgt']} .values()
            ]
        for path
        in  ( glob.glob (os.path.join (opt ['conf'], 'fstab.d', '*'))
            + [os.path.join (opt ['conf'], 'fstab')]
            )
        if os.path.isfile (path) ], [] )) else False

    return ret

# def _mounts ():

# Basically I don't need this one anymore.
# I decided against it for the following reasons:
# 1. There's no way to determine the src when bind mounting.
# 2. You have to readlink everything because you never know if you've a symlink in /dev.

#     return [ dict ( zip ( line.split(), ['src', 'tgt', 'fs', 'opt', 'dummy_1', 'dummy_2'] ))
#             for line in __salt__['cmd.run_all']('cat /proc/mounts')['stdout'].splitlines() ]


def _initctl_machineer_mounts ():
    return  [ dbus.SystemBus().get_object ('com.ubuntu.Upstart', bus_object_path)
            .GetAll ('com.ubuntu.Upstart0_6.Instance'
                , dbus_interface = dbus.PROPERTIES_IFACE)

            for bus_object_path in
            dbus.SystemBus().get_object ( 'com.ubuntu.Upstart'
                , dbus.SystemBus().get_object ('com.ubuntu.Upstart', '/com/ubuntu/Upstart')
                . GetJobByName ( opt['upstart_service_name']
                    , dbus_interface='com.ubuntu.Upstart0_6' )
                )
            . GetAllInstances (dbus_interface='com.ubuntu.Upstart0_6.Job')
            ]

def _initctl_split_name (obj):
    return dict ( zip ( ['src', 'delim-1', 'tgt', 'delim-2', 'options']
        , re.split (opt['upstart_service_separator']
            , obj ['name'] ) ))

def _tree_merge (trees):

    def update(d, u):
        for k, v in u.iteritems():
            if isinstance(v, collections.Mapping):
                r = update(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d

    return reduce (update, trees)
