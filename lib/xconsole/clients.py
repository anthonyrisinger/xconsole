#!/usr/bin/env python2
# coding: utf-8


from __future__ import absolute_import
from __future__ import print_function

import sys
sys.dont_write_bytecode = True

import re
import array
import struct
import operator
import cStringIO

from pprint import (
    pformat as pf,
    pprint as pp,
    )

import mapo
import time
from datetime import datetime

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info(
    '\n%s\n%16s: init: %s\n%s', *(
        '-'*64, __name__, datetime.now(), '-'*64,
        ))


# (reverse) http://stackoverflow.com/questions/8638792
def FP1616(v):
    return v * 65536.0


class Manager(object):

    def __init__(self, w, h, x, y, ptr, name):
        self.name = name
        self.port_map = mapo.record()
        self.event_map = mapo.record()
        self.window_map = mapo.record()
        self.device_map = mapo.record()
        self.controller_map = mapo.record()
        self.connection = None
        #TODO: REMOVE
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)

    @property
    def conn(self):
        if self.connection:
            return self.connection

        conn = self.connection = xcb.connect()
        conn.render = conn(render.key)
        conn.xfixes = conn(xfixes.key)
        conn.xinput = conn(xinput.key)

        conn.render.QueryVersion(0, 11).reply()
        conn.xfixes.QueryVersion(5, 0).reply()
        conn.xinput.XIQueryVersion(2, 3).reply()

        self.root = conn.get_setup().roots[0]

        return self.connection

    def sink_events(self):
        self.conn.core.ChangeWindowAttributesChecked(
            self.root.root, xproto.CW.EventMask, [
                xproto.EventMask.SubstructureRedirect |
                xproto.EventMask.SubstructureNotify
                ]
            ).check()
        self.conn.xinput.XISelectEvents(
            self.root.root, [
                (xinput.Device.All, (
                    xinput.XIEventMask.Hierarchy
                    | xinput.XIEventMask.RawKeyPress
                    | xinput.XIEventMask.RawKeyRelease
                    | xinput.XIEventMask.RawButtonPress
                    | xinput.XIEventMask.RawButtonRelease
                    )),
                ])

    def refresh_devices(self):
        SOL = object()
        stack = list(
            ((info.deviceid, info), self.device_map)
            for info in self.conn.xinput.XIQueryDevice(0).reply().infos
            )

        while stack:
            #...reverse/depth-first allows for list deletes
            (key, attr), node = stack.pop()

            if attr is SOL:
                node.pop(key)
                continue

            if key == 'name':
                attr = ''.join(map(chr, attr)).strip(' \t\n\r\0')
            elif key == 'classes':
                attr = set(vc.type for vc in attr)
            elif hasattr(key, 'endswith'):
                if (key in ('len', 'uninterpreted_data') or
                    key.startswith(('len_', 'num_')) or
                    key.endswith(('_len', '_num'))):
                    attr = SOL

            loop = tuple()
            if attr is SOL:
                stack.append(((key, attr), node))
            elif isinstance(attr, xcb.List):
                attr = list(attr)
                loop = enumerate(attr)
            elif isinstance(attr, xcb.Struct):
                attr = mapo.record(vars(attr))
                loop = attr.iteritems()

            stack.extend((kv, attr) for kv in loop)
            node[key] = attr

        changes = list()
        slots = mapo.record()
        name_re = re.compile('xconsole:([0-9]+)(?! XTEST)')
        for k, v in self.device_map.iteritems():
            match = name_re.match(v.name)
            if match:
                key = int(match.group(1))
                slot = slots[key] = slots.get(key) or [None] * 4
                offset = v.type - 1
                if v.type == 5:
                    offset -= sum(v.classes & {0, 1}, 1)
                slot[offset] = v

        for key, slot in slots.iteritems():
            mptr, mkbd, sptr, skbd = slot
            if None in (mptr, mkbd):
                #...missing mdev(s)
                mdname = 'xconsole:{}'.format(key)
                changes.append((
                    xinput.HierarchyChangeType.AddMaster,
                    1, # send_core
                    0, # enable
                    mdname,
                    ))
            elif 0 in (mptr.enabled, mkbd.enabled):
                #...mdev(s) disabled; FLOAT all sdevs
                for sd in (sptr, skbd):
                    if sd.type != xinput.DeviceType.FloatingSlave:
                        changes.append((
                            xinput.HierarchyChangeType.DetachSlave,
                            sd.deviceid,
                            ))
                #for d in slot:
                #    self.conn.xinput.XIChangePropertyChecked(
                #        d.deviceid,
                #        xproto.PropMode.Replace,
                #        8, # "8Bit"
                #        143, # "Device Enabled"
                #        xproto.Atom.INTEGER,
                #        [0],
                #        ).check()
            elif None not in slot:
                #...devices exist, enable/assoc
                for md, sd in (slot[0::2], slot[1::2]):
                    if sd.attachment != md.deviceid:
                        changes.append((
                            xinput.HierarchyChangeType.AttachSlave,
                            sd.deviceid,
                            md.deviceid,
                            ))

        if changes:
            #NOTE: sdevs either re-enabled on VT switch or re-assoc, DGAF :)
            logger.debug('XIChangeHierarchy: %s', pf(changes, width=40))
            self.conn.xinput.XIChangeHierarchyChecked(changes).check()

        #TODO: XISetClientPointerChecked

    def on_xge(self, event):
        eventmap = {
            13: 'on_raw_key_press',
            14: 'on_raw_key_release',
            15: 'on_raw_button_press',
            16: 'on_raw_button_release',
            }
        if event.xgevent not in eventmap:
            return

        device = self.device_map[event.deviceid]
        if device.type not in (
            xinput.DeviceType.MasterPointer,
            xinput.DeviceType.MasterKeyboard,
            ):
            key = (device.deviceid, 0)
            if 1 in device.classes:
                key = (0, device.deviceid)
            controller = self.next_controller(key)
            handler = getattr(controller, eventmap[event.xgevent], None)
            if handler:
                return handler(event)

    def next_controller(self, key):
        last_controller = self.controller_map.get((0, 0))
        next_controller = self.controller_map.get(key)
        if key[0] == 0:
            return last_controller

        if not next_controller and key[0] != 0:
            next_controller = Controller(self, key)
        if last_controller != next_controller:
            if last_controller:
                last_controller.on_focus_out(next_controller)
            next_controller.on_focus_in(last_controller)
        if next_controller:
            self.controller_map[(0, 0)] = next_controller
        return next_controller

    def main_loop(self):
        self.sink_events()
        self.refresh_devices()
        logger.info(pf(self.device_map, width=1))

        while True:
            try:
                self.conn.flush()
                event = self.conn.wait_for_event()
            except xcb.ProtocolException as e:
                logger.exception(e)
                continue

            except KeyboardInterrupt:
                break

            else:
                logger.debug(
                    '%s:\n%s',
                    event.__class__.__name__,
                    pf(vars(event), width=1),
                    )

            #from IPython import embed as I; I()

            if isinstance(event, xproto.GeGenericEvent):
                self.on_xge(event)
            elif isinstance(event, xproto.MapRequestEvent):
                self.conn.core.MapWindowChecked(event.window).check()
            elif isinstance(event, xproto.ConfigureRequestEvent):
                wm_class = self.conn.core.GetProperty(
                    0,
                    event.window,
                    xproto.Atom.WM_CLASS,
                    xproto.Atom.STRING,
                    0,
                    64,
                    ).reply()
                wm_class = ''.join(map(chr, wm_class.value))
                #logger.info('wm_class: %r', wm_class)
                if wm_class.startswith('Minecraft'):
                    self.window_map[event.window] = mapo.record(vars(
                        conn.core.GetWindowAttributes(event.window).reply()
                        ))
                    port = Port(
                        manager=self,
                        window=event.window,
                        )
                    port.track()
                    #TODO: delay Focus until Map...
                    port.focus()
                    event.value_mask |= (
                        xproto.ConfigWindow.X |
                        xproto.ConfigWindow.Y |
                        xproto.ConfigWindow.Width |
                        xproto.ConfigWindow.Height
                        )
                    x, y, w, h = ( #FIXME
                        self.x,
                        self.y,
                        self.w,
                        self.h,
                        )
                    event.x = x
                    event.y = x
                    event.width = w
                    event.height = h
                if event.border_width > 0:
                    event.value_mask |= xproto.ConfigWindow.BorderWidth
                    event.border_width = 0
                self.conn.core.ConfigureWindowChecked(
                    event.window, event.value_mask, list(
                        getattr(event, key)
                        for key in (
                            'x',
                            'y',
                            'width',
                            'height',
                            'border_width',
                            'sibling',
                            'stack_mode',
                            )
                        if event.value_mask & getattr(
                            xproto.ConfigWindow,
                            key.title().replace('_', ''),
                            )
                        )).check()
            elif isinstance(event, xproto.EnterNotifyEvent):
                pass
            elif isinstance(event, xproto.LeaveNotifyEvent):
                try:
                    self.conn.xinput.XIWarpPointerChecked(
                        0, xid, 0, 0, 0, 0, FP1616(w/2), FP1616(h/2), ptr,
                        ).check()
                except Exception as e:
                    pass

        conn.disconnect()


class Controller(object):

    def __init__(self, manager, key=None):
        self.atoms = mapo.record()
        self.manager = manager
        self.key = key
        self.keycodes = mapo.record(
            need = {37, 50},
            want = {37, 50},
            )

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, k):
        if not k:
            return

        k = self._key = tuple(map(int, k))
        for alt_k in (k, (k[0], 0), (0, k[1])):
            if sum(alt_k) > 0:
                self.manager.controller_map[alt_k] = self

    def __repr__(self):
        return '<{self.__class__.__name__}: {self.key}>'.format(self=self)

    def on_raw_key_press(self, event):
        logger.info(
            'on_raw_key_press: %s %s',
            self, event.detail,
            )
        self.keycodes.want -= {event.detail}

    def on_raw_key_release(self, event):
        logger.info(
            'on_raw_key_release: %s %s',
            self, event.detail,
            )
        if event.detail in self.keycodes.need:
            self.keycodes.want |= {event.detail}

    def on_raw_button_press(self, event):
        logger.info(
            'on_raw_button_press: %s %s %s',
            self, event.detail, event.deviceid,
            )
        if self.key[1] == 0 and not self.keycodes.want:
            self.key = (self.key[0], event.deviceid)
            logger.info('paired: %s', self)

    def on_raw_button_release(self, event):
        logger.info(
            'on_raw_button_release: %s %s %s',
            self, event.detail, event.deviceid,
            )

    def on_focus_in(self, last_controller=None):
        logger.info('on_focus_in: %s', self)
        self.keycodes.want |= self.keycodes.need

    def on_focus_out(self, next_controller=None):
        logger.info('on_focus_out: %s', self)
        self.keycodes.want |= self.keycodes.need


class Port(object):

    def __init__(self, manager, window=None, device=None):
        self.manager = manager
        self.window = window
        self.device = device
        self.manager.port_map[(window, device)] = self

    def track(self):
        mask = (
            xproto.EventMask.EnterWindow |
            xproto.EventMask.LeaveWindow |
            xproto.EventMask.FocusChange
            )

        self.manager.conn.core.ChangeWindowAttributesChecked(
            self.window,
            xproto.CW.EventMask,
            [mask],
            ).check()

        #self.manager.conn.xinput.XISetClientPointerChecked(
        #    self.window,
        #    self.device,
        #    ).check()

    def focus(self):
        focus_event = struct.pack('BB2xIB23x', 9, 0, self.window, 0)
        self.manager.conn.core.SendEventChecked(
            0,
            self.window,
            xproto.EventMask.FocusChange,
            focus_event,
            ).check()


#FIXME: workarounds to incomplete library generation ------------------#

import xcb.xcb
_xcb = xcb.xcb

#...avoid deprecated 2.x relative import semantics
xcb.__dict__.update(_xcb.__dict__)
sys.modules['xcb.xcb'] = xcb

#...save a copy of parent for manual unpacking
class Struct(_xcb.Struct):

    def __init__(self, parent, *args):
        _xcb.Struct.__init__(self, parent, *args)
        self.__parent__ = parent

class Reply(_xcb.Reply):

    def __init__(self, parent, *args):
        _xcb.Reply.__init__(self, parent, *args)
        self.__parent__ = parent
        self.response_type = struct.unpack_from('=B', parent)[0]

class Event(_xcb.Event):

    __xge__ = mapo.automap()
    __xge__[131][11]['xx2x4x2xHIIH10x'].update(enumerate((
        'deviceid',
        'time',
        'flags',
        'num_infos',
        )))
    __xge__[131][13]['xx2x4x2xHIIHHI4x'].update(enumerate((
        'deviceid',
        'time',
        'detail',
        'sourceid',
        'valuators_len',
        'flags',
        )))
    __xge__[131][14] = __xge__[131][13]
    __xge__[131][15] = __xge__[131][13]
    __xge__[131][16] = __xge__[131][13]

    def __init__(self, parent, *args):
        _xcb.Event.__init__(self, parent, *args)
        cls = self.__class__
        ns = mapo.record()
        ns.response_type, ns.extension = (
            struct.unpack_from('=BB', parent)
            )

        if ns.response_type == 35 and ns.extension in cls.__xge__:
            (ns.xgevent,) = struct.unpack_from('=8xH', parent)
            fmt = str()
            attrs = list()
            info = cls.__xge__[ns.extension][ns.xgevent]
            if info:
                (fmt, attrs), = info.viewitems()
                ns.update(zip(
                    (attrs[i] for i in range(len(attrs))),
                    struct.unpack_from(fmt, parent),
                    ))

        for key, attr in ns.iteritems():
            setattr(self, key, attr)

        return self

#...BEFORE core/extension import!
xcb.Struct = Struct
xcb.Reply = Reply
xcb.Event = Event

from xcb import (
    xproto,
    render,
    xfixes,
    xinput,
    )

def XISelectEvents(self, window, masks):
    buf = cStringIO.StringIO()
    buf.write(struct.pack('=xx2xIH2x', window, len(masks)))
    for deviceid, mask in masks:
        buf.write(struct.pack('=HHI', deviceid, 1, mask))
    return self.send_request(
        xcb.Request(buf.getvalue(), 46, True, False),
        xcb.VoidCookie(),
        )

def _XIChangeProperty(self, chk, devid, mode, form, prop, typ, items):
    fmt = {8: 'B', 16: 'H', 32: 'I'}
    buf = cStringIO.StringIO()
    buf.write(struct.pack(
        '=xx2xHBBIII', devid, mode, form, prop, typ, len(items),
        ))
    buf.write(struct.pack(
        '={0}{1}'.format(len(items), fmt[form]),
        *items
        ))
    return self.send_request(
        xcb.Request(buf.getvalue(), 57, True, chk),
        xcb.VoidCookie(),
        )

def XIChangeProperty(self, *ch):
    return _XIChangeProperty(self, False, *ch)

def XIChangePropertyChecked(self, *ch):
    return _XIChangeProperty(self, True, *ch)

def _XIChangeHierarchy(self, chk, changes):
    fmt = {
        1: _XIChangeHierarchy_AddMaster,
        2: '',
        3: '=HHHH',
        4: '=HHH2x',
        }
    buf = cStringIO.StringIO()
    buf.write(struct.pack('=xx2xB3x', len(changes)))
    for ch in changes:
        ch, chtyp = ch[1:], ch[0]
        chfmt = fmt[chtyp]
        if hasattr(chfmt, '__call__'):
            ch, chfmt = chfmt(*ch)
        chsz = struct.calcsize(chfmt)
        chbuf = struct.pack(chfmt, chtyp, chsz/4, *ch)
        buf.write(chbuf)
    return self.send_request(
        xcb.Request(buf.getvalue(), 43, True, chk),
        xcb.VoidCookie(),
        )

def _XIChangeHierarchy_AddMaster(send_core, enable, name):
    nl = len(name)
    return (nl, send_core, enable, name), '=HHHBB{}s'.format(nl + (nl % 4))

def XIChangeHierarchy(self, *ch):
    return _XIChangeHierarchy(self, False, *ch)

def XIChangeHierarchyChecked(self, *ch):
    return _XIChangeHierarchy(self, True, *ch)

xinput.xinputExtension.XISelectEvents = XISelectEvents
xinput.xinputExtension.XIChangeProperty = XIChangeProperty
xinput.xinputExtension.XIChangePropertyChecked = XIChangePropertyChecked
xinput.xinputExtension.XIChangeHierarchy = XIChangeHierarchy
xinput.xinputExtension.XIChangeHierarchyChecked = XIChangeHierarchyChecked

#----------------------------------------------------------------------#


if __name__ == '__main__':
    manager = Manager(*sys.argv[1:])
    conn = manager.conn #FIXME
    manager.main_loop()
