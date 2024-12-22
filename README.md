# automated_mixer_old
The first proof-of-concept (quick, rudimentary script) for automated audio mixing using pyaudacity.

Objective: automate the process of mixing tracks (layering) from given files
Input Rules
    - folder of ffmpeg-compatible files (filepath string) 

Mix rules:
- Length mode
    - Longest: In this mode, find the longest file in the input folder and make the output file that length
    - Repeat files shorter than the target length until the track's audio is at least as long as the target length. Trim the excess.
 
Execution:

python3 automated_bundles.py [input dir]
