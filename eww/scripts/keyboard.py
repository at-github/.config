#!/usr/bin/env python3
"""Print the keyboard layout and Caps Lock state as JSON, now and on each change
(for deflisten).

Listens to XKB events through libX11 (python-xlib has no XKB support): lock
changes for Caps Lock, new keyboard or name changes for the layout (setxkbmap).
"""
import ctypes
import json
import subprocess

XKB_USE_CORE_KBD = 0x0100
XKB_NEW_KEYBOARD_NOTIFY = 0
XKB_STATE_NOTIFY = 2
XKB_NAMES_NOTIFY = 6
XKB_MODIFIER_LOCK_MASK = 1 << 3
XKB_ALL_NAMES_MASK = 0x3FFF
XKB_ALL_NEW_KEYBOARD_EVENTS_MASK = 0x7
LOCK_MASK = 1 << 1


class XkbAnyEvent(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_int),
        ("serial", ctypes.c_ulong),
        ("send_event", ctypes.c_int),
        ("display", ctypes.c_void_p),
        ("time", ctypes.c_ulong),
        ("xkb_type", ctypes.c_int),
        ("device", ctypes.c_uint),
    ]


class XEvent(ctypes.Union):
    # XEvent is 24 longs
    _fields_ = [("xkb", XkbAnyEvent), ("pad", ctypes.c_long * 24)]


class XkbStateRec(ctypes.Structure):
    _fields_ = [
        ("group", ctypes.c_ubyte),
        ("locked_group", ctypes.c_ubyte),
        ("base_group", ctypes.c_ushort),
        ("latched_group", ctypes.c_ushort),
        ("mods", ctypes.c_ubyte),
        ("base_mods", ctypes.c_ubyte),
        ("latched_mods", ctypes.c_ubyte),
        ("locked_mods", ctypes.c_ubyte),
        ("compat_state", ctypes.c_ubyte),
        ("grab_mods", ctypes.c_ubyte),
        ("compat_grab_mods", ctypes.c_ubyte),
        ("lookup_mods", ctypes.c_ubyte),
        ("compat_lookup_mods", ctypes.c_ubyte),
        ("ptr_buttons", ctypes.c_ushort),
    ]


xlib = ctypes.CDLL("libX11.so.6")
xlib.XOpenDisplay.restype = ctypes.c_void_p
xlib.XOpenDisplay.argtypes = [ctypes.c_char_p]
xlib.XkbQueryExtension.argtypes = [ctypes.c_void_p] + [ctypes.POINTER(ctypes.c_int)] * 5
xlib.XkbSelectEventDetails.argtypes = [
    ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_ulong, ctypes.c_ulong,
]
xlib.XkbGetState.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.POINTER(XkbStateRec)]
xlib.XNextEvent.argtypes = [ctypes.c_void_p, ctypes.POINTER(XEvent)]


def layout():
    """Variant if any (bepo), layout otherwise."""
    query = subprocess.run(["setxkbmap", "-query"], capture_output=True, text=True).stdout
    fields = dict(line.split(":", 1) for line in query.splitlines() if ":" in line)
    return (fields.get("variant") or fields.get("layout", "")).strip()


def caps(display):
    state = XkbStateRec()
    xlib.XkbGetState(display, XKB_USE_CORE_KBD, ctypes.byref(state))
    return bool(state.locked_mods & LOCK_MASK)


def main():
    display = xlib.XOpenDisplay(None)
    if not display:
        raise SystemExit("cannot open display")
    opcode, event_base, error_base = ctypes.c_int(), ctypes.c_int(), ctypes.c_int()
    major, minor = ctypes.c_int(1), ctypes.c_int(0)
    if not xlib.XkbQueryExtension(
        display, opcode, event_base, error_base, major, minor
    ):
        raise SystemExit("no XKB extension")
    xlib.XkbSelectEventDetails(
        display, XKB_USE_CORE_KBD, XKB_STATE_NOTIFY,
        XKB_MODIFIER_LOCK_MASK, XKB_MODIFIER_LOCK_MASK,
    )
    xlib.XkbSelectEventDetails(
        display, XKB_USE_CORE_KBD, XKB_NAMES_NOTIFY,
        XKB_ALL_NAMES_MASK, XKB_ALL_NAMES_MASK,
    )
    xlib.XkbSelectEventDetails(
        display, XKB_USE_CORE_KBD, XKB_NEW_KEYBOARD_NOTIFY,
        XKB_ALL_NEW_KEYBOARD_EVENTS_MASK, XKB_ALL_NEW_KEYBOARD_EVENTS_MASK,
    )

    current = {"layout": layout(), "caps": caps(display)}
    print(json.dumps(current), flush=True)
    event = XEvent()
    while True:
        xlib.XNextEvent(display, ctypes.byref(event))
        if event.xkb.type != event_base.value:
            continue
        state = dict(current, caps=caps(display))
        if event.xkb.xkb_type in (XKB_NEW_KEYBOARD_NOTIFY, XKB_NAMES_NOTIFY):
            state["layout"] = layout()
        if state != current:
            print(json.dumps(state), flush=True)
            current = state


if __name__ == "__main__":
    main()
