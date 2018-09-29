#!/bin/sh

mkdir -p ~/.local/share/gedit/plugins
cp transposer.* ~/.local/share/gedit/plugins

echo "Plugin installed! Now restart gedit and active it in Edit > Preferences."
