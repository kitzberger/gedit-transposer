from gettext import gettext as _
from gi.repository import GObject, Gtk, Gedit
import re
import pprint

# Menu item example, insert a new item in the Tools menu
ui_str = """<ui>
    <menubar name="MenuBar">
        <menu name="ToolsMenu" action="Tools">
            <placeholder name="Transpose">
                <menuitem name="TransposeUp" action="TransposeUp"/>
                <menuitem name="TransposeDown" action="TransposeDown"/>
            </placeholder>
        </menu>
    </menubar>
    <toolbar name="ToolBar">
        <separator />
        <toolitem name="TransposeToolItemUp" action="TransposeUp" />
        <toolitem name="TransposeToolItemDown" action="TransposeDown" />
    </toolbar>
</ui>
"""
class TransposerWindowActivatable(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "TransposerWindowActivatable"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        # Insert menu items
        self._insert_menu()

    def do_deactivate(self):
        # Remove any installed menu items
        self._remove_menu()

        self._action_group = None

    def _insert_menu(self):
        # Get the Gtk.UIManager
        manager = self.window.get_ui_manager()

        # Create a new action group
        self._action_group = Gtk.ActionGroup("TransposerPluginActions")
        self._action_group.add_actions([
            ("TransposeUp", None, _("Transpose chords by +1"), None, _("Transpose chords by +1"), lambda e: self.on_transpose(None, 1)),
            ("TransposeDown", None, _("Transpose chords by -1"), None, _("Transpose chords by -1"), lambda e: self.on_transpose(None, -1))
        ])

        # Insert the action group
        manager.insert_action_group(self._action_group, -1)

        # Merge the UI
        self._ui_id = manager.add_ui_from_string(ui_str)

    def _remove_menu(self):
        # Get the Gtk.UIManager
        manager = self.window.get_ui_manager()

        # Remove the ui
        manager.remove_ui(self._ui_id)

        # Remove the action group
        manager.remove_action_group(self._action_group)

        # Make sure the manager updates
        manager.ensure_update()

    def do_update_state(self):
        self._action_group.set_sensitive(self.window.get_active_document() != None)

    # Menu activate handlers
    def on_transpose(self, action, transposeBy):
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

        doc.set_text(stringAfter.rstrip())

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
