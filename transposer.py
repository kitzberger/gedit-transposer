from gettext import gettext as _
from gi.repository import GObject, Gtk, Gedit
import re
import pprint

# Menu item example, insert a new item in the Tools menu
ui_str = """<ui>
  <menubar name="MenuBar">
    <menu name="ToolsMenu" action="Tools">
      <placeholder name="ToolsOps_2">
        <menuitem name="Transposer" action="Transposer"/>
      </placeholder>
    </menu>
  </menubar>
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
        self._action_group.add_actions([("Transposer", None, _("Transpose chords by +1"),
                                         None, _("Transpose chords by +1"),
                                         self.on_transpose_document)])

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
    def on_transpose_document(self, action):
        doc = self.window.get_active_document()

        if not doc:
            return

        start, end = doc.get_bounds()
        string = doc.get_text(start, end, True)
#       print "String found: \n" + string

        # ^\s*([ABHCDEFG]+[b#]?m?[79]?\s*)*$
        pattern = r'^\s*([ABCDEFG]+[b#]?m?[679]?\s*)+$'

        string = re.sub(pattern, transpose_chord_line, string, 0, re.M | re.I)
        
        doc.set_text(string)

def transpose_chord_line(matchObj):
    string = matchObj.group(0)
    print "Transposing line '" + string + "':"
    string = re.sub(r'([ABCDEFG][^\s]*(\s|$)?)', transpose_chord, string, re.M | re.I)
    print "Done. Now it is: '" + string + "'.\n"
    return string

#
# matchObj.group(0):
# - E.
# - Dm
# - H7
# - Bb
# - A#m7
#
def transpose_chord(matchObj):
    chord = matchObj.group(0)
    len_chord = len(chord)
    #print "\n\n'"+chord+"'"

    chord = re.match(r'([ABCDEFG][b#]?)(.*)', chord, re.M | re.I)
    note = chord.group(1)

    transpose = 1
    halftones = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

    index = halftones.index(note)
    newindex = (index+transpose) % len(halftones)

    newchord = halftones[newindex] + chord.group(2)
    if len(newchord) != len_chord:
        if len(newchord) < len_chord:
            newchord += ' '
        else:
            if newchord[-1:] == ' ':
                newchord = newchord[:-1]

    #print "- transpose '" + chord.group(0) + "' by " + str(transpose) + " to '" + newchord + "'"

    return newchord