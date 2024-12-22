import pyaudacity as pa
import os
import math
import string
import sys
import shutil
import mutagen
from mutagen.mp4 import MP4
from mutagen.mp3 import MP3
from mutagen.wave import WAVE


audio_dir = './'
output_dir = './'
working_dir_path = "wd"

def load_audio(audio_fp):
    if 'mp3' in audio_fp:
            return MP3(audio_fp)
    elif 'm4a' in audio_fp:
            return MP4(audio_fp)
    elif 'wav' in audio_fp:
            return WAVE(audio_fp)

#check audio files in given dir and report if any are invalid format
def check_audio_files():
    audio_list = os.listdir(os.path.abspath(audio_dir))
    invalid_audio = []
    for audio_fn in audio_list:
        parts = os.path.splitext(audio_fn)
        valid = "mp3" in parts[1] or 'm4a' in parts[1] or 'wav' in parts[1]
        if not valid:
            invalid_audio.append(audio_fn)
    return invalid_audio
        
#create a new working dir and copy files over
def working_dir_copy():
    if (os.path.exists(working_dir_path)):
        shutil.rmtree(working_dir_path)
    os.mkdir(working_dir_path)
    audio_list = os.listdir(audio_dir)
    for idx, audio_fn in enumerate(audio_list):
        fp_parts = os.path.splitext(audio_fn)
        orig_fp = os.path.join(os.path.abspath(audio_dir), audio_fn)
        new_fn = str(idx) + fp_parts[1]
        new_fp = os.path.join(os.path.abspath(working_dir_path), new_fn)
        shutil.copy(orig_fp, new_fp)

def import_files():
    invalid_files = check_audio_files()
    
    if (len(invalid_files) > 0):
        print("These audio files are invalid\n")
        for file in invalid_files:
            print(file)
        sys.exit()
    
    working_dir_copy()
                            
    durations = {}
    audio_list = os.listdir(os.path.abspath(working_dir_path))
    for audio_idx, audio_fn in enumerate(audio_list):
        #for each file, import it as a separate track
        audio_fp = os.path.join(os.path.abspath(working_dir_path), audio_fn)
        macro_fp = '"' + audio_fp  + '"'
        macro = 'Import2: Filename=' + macro_fp
        pa.do(macro)
        #store duration of file in dictionary
        audio = load_audio(audio_fp)
        if (audio != None):
            audio_info = audio.info
            length = int(audio_info.length)
            durations[audio_idx] = length
    return durations

def repeater(track_no, track_length, target_l):
    macro = 'SelectTracks:Track=' + str(track_no) + ' Mode=Set TrackCount=1'
    pa.do(macro)
    macro = 'SelTrackStartToEnd'
    pa.do(macro)
    #calculate how many times to repeat selected track
    repeat_no = math.ceil(target_l / track_length)
    
    #repeat by repeat_no dvcfxb
    repeat_str = str(repeat_no - 1)
    print(repeat_str)
    macro = "Repeat:Count=" + repeat_str
    pa.do(macro)
    #calculate length of track after repeats
    tr_l = track_length * repeat_no
    offset = tr_l - target_l
    if offset > 0:
        trim_excess(track_no, offset)

def trim_excess(track_no, offset):
    macro = 'SelectTracks:Track=' + str(track_no) + ' TrackCount=1'
    pa.do(macro)
    macro = 'SelectTime:Start=' + str(offset) + ' RelativeTo=SelectionEnd'
    pa.do(macro)
    #macro = 'CursSelStart'
    #pa.do(macro)
    macro = 'SelCursorToTrackEnd'
    pa.do(macro)
    macro = 'Delete'
    pa.do(macro)

def adjust_tracks(tracks_lengths, target_l):
    for (track, length) in tracks_lengths:
        #print(track, length)
        if length < target_l:
            repeater(track, length, target_l)
        else:
            #print('equal length')
            continue

def gen_bundle():
    #opens a new fresh window
    pa.new()
    #import all the audio files - (including silencer)
    #will return the length of each bundled file except the silencer
    durations = import_files()
    print(durations)
    #identify target length (mode dependent)
    sorted_durations = sorted(durations.items(), key=lambda x:x[1])
    tl = list(sorted_durations)[-1][1]
    print("Target length=", tl)
    #adjust all tracks to target length
    adjust_tracks(sorted_durations, tl)

    shutil.rmtree(working_dir_path)


if __name__  == "__main__":
    
    audio_dir = os.path.abspath(sys.argv[1])

    #test out change tempo
    gen_bundle()
