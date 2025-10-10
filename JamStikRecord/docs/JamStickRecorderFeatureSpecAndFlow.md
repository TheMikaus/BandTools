# Features
- Read the notes in real time from the JamStik studio midi guitar
- Output Music XML file
- Flashing, clicking metronome
- Live Guitar tab
- Export guitar tab


fretted notes: When you fret a note, the Jamstik sends a "Note-On" message. This message contains a note number that corresponds to the specific note and fret position, and a velocity value based on how hard you picked the string. When you lift your finger, it sends a "Note-Off" message.
Individual string data: Using a multi-channel or MPE (MIDI Polyphonic Expression) mode, the Jamstik can send MIDI data for each string on its own separate channel. This is especially useful for creating unique sounds for each string or for applications that require per-string expression.
Performance nuances: The Jamstik can also transmit other performance information, including:
String bend: Transmits pitch bend messages when a string is bent.
Aftertouch/string envelope: Detects the amplitude of a note over time and sends this as a MIDI message, which can be mapped to control volume or other parameters.
Expression tracking: This allows for dynamic control of sounds that follow the decay and vibrato of your playing
