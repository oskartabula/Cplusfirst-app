import xml.etree.ElementTree as ET
import os
import csv

def loadmcrlists():
    mcrlists_list = []
    for file in os.listdir():
        if file.endswith(".MCRList"):
            files = list([file])
            mcrlists_list.extend(files)
    return mcrlists_list

def timecode_toframes(timecode):
    hours = int(timecode.split(":")[0])
    minutes = int(timecode.split(":")[1])
    seconds = int(timecode.split(":")[2])
    frames = int(timecode.split(":")[3])
    return frames + seconds*25 + minutes*1500 + hours*9000

def frames_totimecode(totalframes):
    hours = int(totalframes / 90000)
    minutes = int(totalframes % 90000 / 1500)
    seconds = int(totalframes % 1500 / 25)
    frames = int(totalframes % 25)
    return  f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"


def framediff(timecode1, timecode2):
    diff = timecode_toframes(timecode1) - timecode_toframes(timecode2)
    diff_timecode = frames_totimecode(diff)
    return abs(diff)


def load_durationdb(durationDB_url):
    duration_base = {}
    with open(durationDB_url) as durationDB:
        next(durationDB)
        for row in csv.reader(durationDB, delimiter=','):
            if len(row) >= 2 and len(row[1]) == 11:
                duration_base[row[0]] = row[1]
            else:
                continue
        return duration_base

def load_playlist(playlist_url):
    playlist = {}
    root = ET.parse(playlist_url).getroot()
    for item in root.iter('item'):
        src_out, itemname, start = item.get('src_out'), item.get('name'), item.get('start')
        for timeline in item.iter('quality'):
            if len(timeline.get("src")) > 10 and len(src_out) == 11:
                path, fileext = timeline.get("src").split('.')[0].split("\\")[2], timeline.get("src").split('.')[-1]
                if fileext == 'mp4':
                    playlist[path] = src_out
    return playlist

def check_playlist(playlist, duration_base):
    wrongdur_list = []
    notinDB_list = []
    is_ok = False
    for mediaID in playlist.keys():
        if mediaID in duration_base.keys():
            differance = framediff(playlist.get(mediaID), duration_base.get(mediaID))
            if differance <= 1:

                correct_dict[mediaID] = playlist.get(mediaID)
            else:
                print(f'{mediaID} ma niezgodny czas trwania, który wynosi {playlist.get(mediaID)}, zamiast {duration_base.get(mediaID)}, różnica to {differance} klatek')
                wrongdur_dict[mediaID] = playlist.get(mediaID)
                wrongdur_list.append(mediaID)
        else:
            print(f'{mediaID} nie ma w bazie')
            notinDB_dict[mediaID] = playlist.get(mediaID)
            notinDB_list.append(mediaID)
    if len(wrongdur_list) + len(notinDB_list) == 0:
        is_ok = True
    return is_ok


wrongdur_dict = {}
notinDB_dict = {}
correct_dict = {}
durationDB_url = 'All files durations.csv'
duration_base = load_durationdb(durationDB_url)

for mcrlist in loadmcrlists():
    playlist = load_playlist(mcrlist)
    print(f'\n\nSprawdzanie playlisty: {mcrlist}...')
    result = check_playlist(playlist, duration_base)
    if result == True:
        print(f"Playlista jest ok!")

print('\n\nPoniższe MediaID mają zły czas:')
for wpis in wrongdur_dict:
    print(f'{wpis} {wrongdur_dict.get(wpis)} zamiast {duration_base.get(wpis)}')
print('\n\nPoniższych MediaID nie ma w bazie:')
for wpis in notinDB_dict:
    print(wpis, notinDB_dict.get(wpis))
input()
