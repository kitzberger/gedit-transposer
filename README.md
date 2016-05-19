# gedit-transposer

This plugin for gedit enables to transpose chords within a text document by single half notes.

You can trigger the up resp. down transposing by clicking the items in the 'Tools' menu or by pressing Ctrl+Alt+u resp. Ctrl+Alt+d.

![Screenshot of new menu items](screenshot.png?raw=true)

The tool will then try to detect lines that contain chords and transpose them accordingly. It should cover quite a variety of chords types, such as Am, C/G and even weird ones like Fmaj7#11. Please let me know if I missed some so I can improve the algorithm.

The tool also distinguishes between lines that are using spaces to 'position' the chords above some text and those that don't do that and just space separate the chords. In the first case it tries to adjust the amount of spaces so the chord positions won't change. In the latter case it doesn't do any magic to the spaces between them.

Original example file:
```
Lorem Ipsum - Unknown Artist
============================

Capo II

 F                              C
Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
 F                               G
sed diam nonumy eirmod tempor invidunt ut labore et dolore
 Am                              C
magna aliquyam erat, sed diam voluptua. At vero eos et
Am                                  F/C
accusam et justo duo dolores et ea rebum. Stet clita kasd
```
After transposing by two half notes:
```
Lorem Ipsum - Unknown Artist
============================

Capo II

 G                              D
Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
 G                               A
sed diam nonumy eirmod tempor invidunt ut labore et dolore
 Bm                              D
magna aliquyam erat, sed diam voluptua. At vero eos et
Bm                                  G/D
accusam et justo duo dolores et ea rebum. Stet clita kasd
```

Compatible with gedit >= 3.12 (presumably)

## Known Issues

* A line with 'positioned' chords that contains chords with only one space between them will cannot fully be transposed without losing those spaces

## Thanks

* Kudos to Guillaume Chereau and his plugin [gedit-reflow-plugin](https://github.com/guillaumechereau/gedit-reflow-plugin) that helped a great deal when trying to upgrade my plugin to the latest gedit API
