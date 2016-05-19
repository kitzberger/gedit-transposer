from gettext import gettext as _
from gi.repository import GObject, Gtk, Gio, Gedit
import re
import pprint

ACTIONS = {
    'transposeUp': {
        'label': _("Transpose chords up"),
        'key':   ['<Ctrl><Alt>u']
    },
    'transposeDown': {
        'label': _("Transpose chords down"),
        'key':   ['<Ctrl><Alt>d']
    }
}

class GeditTransposerApp(GObject.Object, Gedit.AppActivatable):
    __gtype_name__ = "GeditTransposerApp"
    app = GObject.property(type=Gedit.App)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        # Single menu items & shortcuts
        self.menu_ext = self.extend_menu("tools-section")
        for action, config in ACTIONS.items():
            item = Gio.MenuItem.new(config['label'], "win.%s" % action)
            self.menu_ext.prepend_menu_item(item)
            self.app.set_accels_for_action("win.%s" % action, config['key'])

    def do_deactivate(self):
        for action, config in ACTIONS.items():
            self.app.set_accels_for_action("win.%s" % action, [])
        del self.menu_ext

class GeditTransposerWindowActivatable(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "GeditTransposerWindow"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        try:
            action = Gio.SimpleAction(name="transposeUp")
            action.connect('activate', lambda e,f: self.on_transpose(1))
            self.window.add_action(action)
            action = Gio.SimpleAction(name="transposeDown")
            action.connect('activate', lambda e,f: self.on_transpose(-1))
            self.window.add_action(action)
        except Exception as msg:
            import traceback
            print("Error initializing \"Transposer\" plugin")
            print(traceback.print_exc())

    def do_update_state(self):
        for action, config in ACTIONS.items():
            self.window.lookup_action(action).set_enabled(self.window.get_active_document() is not None)

    # Menu activate handlers
    def on_transpose(self, transposeBy):
        doc = self.window.get_active_document()

        if not doc:
            print("No doc found!")
            return

        start, end = doc.get_bounds()

        string = doc.get_text(start, end, True)
        # print("String found: \n" + string)

        stringAfter = ''
        pattern = r'^\s*([ABHCDEFG]+[b#]?(m|sus|add|dim|maj|aug|2|3|4|5|6|7|9|11|13|#5|b5|b9|#9|#11){0,4}(\/[ABHCDEFG][b#]?)?[\s,]*)+$'
        for line in string.split('\n'):
            stringAfter += re.sub(pattern, lambda matchObj: transpose_chord_line(matchObj, transposeBy), line, 0, re.I) + "\n"

        # Position cursor to beginning of document before starting the text alteration
        doc.place_cursor(start)

        # Change text as one user action (undo/redo-able action)
        doc.begin_user_action()
        doc.set_text(stringAfter.rstrip())
        doc.end_user_action()

        # Reposition cursor to beginning of document
        start, end = doc.get_bounds()
        doc.place_cursor(start)

def transpose_chord_line(matchObj, transposeBy):
    string = matchObj.group(0)
    print("Transposing line '" + string + "':")

    keepSpacesUntouched = False
    if re.search(r'[ ]{2}', string, re.I) is None:
        keepSpacesUntouched = True

    # Process each chord (incl. following whitespace)
    string = re.sub(r'([ABHCDEFG][^\s]*\s{0,2})', lambda matchObj: transpose_chord(matchObj, transposeBy, keepSpacesUntouched), string, 0, re.I)

    print("Done. Now it is: '" + string.rstrip() + "'.\n")
    return string.rstrip()

#
# matchObj.group(0):
# - E
# - Dm
# - H7
# - Bb
# - A#m7
# - ...
#
def transpose_chord(matchObj, transposeBy, keepSpacesUntouched):
    if type(matchObj) is str:
        chord = matchObj
    else:
        chord = matchObj.group(0)

    len_chord = len(chord)

    # Full chords
    chord = re.match(r'([ABHCDEFG][b#]?)([^\/]*)(\/)?(.*)?', chord, re.I)
    # Root note only
    note = chord.group(1)
    # Appendix, e.g. '7', 'm7' or 'sus2'
    appendix = chord.group(2)
    # Optional bass note
    bass = chord.group(4)

    if bass:
        # transpose bass note only and keepSpacesUntouched=True
        # since the spaces will be handled for the full chord later.
        bass = '/' + transpose_chord(bass, transposeBy, True)

    halftones = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
    # special handling for german H
    if note == 'H':
        halftones = ['A', 'Bb', 'H', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

    index = halftones.index(note)
    newindex = (index+transposeBy) % len(halftones)

    newchord = halftones[newindex] + appendix + bass

    # in case the new chord lost or gained a 'b' or '#'
    if not keepSpacesUntouched and len(newchord) != len_chord:
        diff = len_chord-len(newchord)
        # in case the new chord lost something,
        # add one or more spaces after it
        if diff > 0:
            newchord += ' '*diff
        # in case the new chord has gained length
        else:
            # and it's one or more tailing spaces,
            # cut off the diff-numbered spaces
            while diff < 0:
                diff += 1
                if newchord[-1:] == ' ':
                    newchord = newchord[:-1]

    print("- transpose " + ("'" + chord.group(0) + "'").ljust(15) + " by " + str(transposeBy) + " to '" + newchord + "'" + (""," (keepSpacesUntouched)")[keepSpacesUntouched])

    return newchord
