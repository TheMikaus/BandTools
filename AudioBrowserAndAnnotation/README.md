# What is this tool for?
This tool is to help with listening, critiquing, and cataloging a band's band practices. It's to make the weekly task of listening through a practice easier to manage.

# What are the features of the tool? (several features need to be retested)
- Can play, stop, scrub through a wave or mp3 file.
- Can give the file a song name/meta name
- Can bulk rename the folder based off of the song name/meta names provided
- Can leave a comment at a specific timestamp in the file (an annotation)
- Can mark that annotation as "important"
- Per folder can see all important annotations in one spot, as well as an overall comment
- Can bulk convert wave -> mp3 if you have ffmpeg installed
- Can create a clip of a file. This is like an annotation that spans a timeframe.
- Can export the clip as a separate file
- Each user can have their own annotation file
- Multiple annotation files can live in a directory, and be visible in the application allowing each bandmate to make their own comments
- Can export the annotations to a text file 
- Has an undo chain

# Expected Workflow
- Have band practice. Record each song as a separate audio file.
- Create a new dated folder in the practice files folder
- In the library tab click on the file name to start playing, put the name of the song in the provided name column. Do this for all songs.
- Click "Batch Rename" to convert the files to the proper names.
- Listen to each song, leaving annotations, and selecting clips of parts of the song that really stand out.

# Note
- Basically this whole application is ChatGPT or CoPilot generated. The idea was just to have it generate a tool so I can have my workflows go faster.
- Trying to figure out how I want a cloud based storage would work
- Once I've finished feature creep on the application I plan on trying to refactor it into to more than one file.
- Maybe have CoPilot add unit test like things.
