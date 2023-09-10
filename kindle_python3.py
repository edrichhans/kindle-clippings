#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import json
import os
import re

BOUNDARY = u"==========\r\n"
DATA_FILE = u"clips.json"
OUTPUT_DIR = u"output"


def get_sections(filename):
    with open(filename, 'rb') as f:
        content = f.read().decode('utf-8')
    content = content.replace(u'\ufeff', u'')
    return content.split(BOUNDARY)


def get_clip(section: str):
    clip = {}

    lines = [l for l in section.split(u'\r\n') if l]
    if len(lines) != 3:
        return

    clip['book'] = lines[0]
    match = re.search(r'(\d+)-\d+', lines[1])
    
    position = 0
    if match:
        position = match.group(1)
    else:
        # some notes has only 1 page location
        match = re.search(r'Location \d+', lines[1])
        if match:
            position = match.group(0).split(' ')[1]
        else:
            print("Error parsing position: %s" % lines[1])
            return

    clip['position'] = int(position)

    # If it's a note, add a > to the beginning of the note
    if lines[1].find("- Your Note on ") != -1:
        clip['content'] = ">" + lines[2]
    else:
        clip['content'] = lines[2]

    # Append position
    clip['content'] += " (Loc. %s)" % position

    return clip


def export_txt(clips):
    """
    Export each book's clips to single text.
    """
    for book in clips:
        lines = []
        for pos in sorted(clips[book], key=int):
            lines.append(clips[book][pos].encode('utf-8'))

        filename = os.path.join(OUTPUT_DIR, u"%s.md" % book)

        with open(filename, 'wb') as f:
            f.write(b"\n\n".join(lines))


def load_clips():
    """
    Load previous clips from DATA_FILE
    """
    try:
        with open(DATA_FILE, 'rb') as f:
            return json.load(f)
    except (IOError, ValueError):
        return {}


def save_clips(clips):
    """
    Save new clips to DATA_FILE
    """
    # with open(DATA_FILE, 'wb') as f:
    # with open(DATA_FILE, 'wb') as f:
    with open(DATA_FILE, 'w') as f:
        json.dump(clips, f)


def main():
    # load old clips
    clips = collections.defaultdict(dict)
    clips.update(load_clips())

    # extract clips
    sections = get_sections(u'My Clippings.txt')
    for section in sections:
        clip = get_clip(section)
        if clip:
            clips[clip['book']][str(clip['position'])] = clip['content']

    # remove key with empty value
    clips = {k: v for k, v in clips.items() if v}

    # save/export clips
    save_clips(clips)
    export_txt(clips)


if __name__ == '__main__':
    main()
