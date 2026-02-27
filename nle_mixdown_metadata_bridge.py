# nle_mixdown_metadata_bridge.py
# Version: 1.0.0
# Author: Sebastian Schmidt
# Copyright (C) 2026 Sebastian Schmidt
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <https://www.gnu.org/licenses>.
#
# Runs directly in the Resolve Console
#!/usr/bin/env python

"""
nle_mixdown_metadata_bridge.py
Copies clip names from an imported offline EDL (Track 2)
to both scene-detected mixdown clips (Track 1)
and the Camera Notes column in the Media Pool.
Also copies Source Start TC from Track 2 into 'Audio Aux 1 TC'.
Clips with mismatched durations or missing counterparts are highlighted in orange on Track 1.
"""

from python_get_resolve import GetResolve
resolve = app.GetResolve()

# You can run the code below directly from the console. Switch Console to Python 3 before.
pm = resolve.GetProjectManager()
project = pm.GetCurrentProject()
timeline = project.GetCurrentTimeline()

if not timeline:
    print("No timeline is currently open.")
    exit()

# Get timeline framerate
fps = timeline.GetSetting("timelineFrameRate")
print(f"Timeline framerate detected: {fps} fps\n")

# Tracks: Track 1 receives names from Track 2
track_v1 = 1
track_v2 = 2

clips_v1 = timeline.GetItemListInTrack("video", track_v1)
clips_v2 = timeline.GetItemListInTrack("video", track_v2)

print(f"Track V1: {len(clips_v1)} clips")
print(f"Track V2: {len(clips_v2)} clips\n")

def seconds_to_tc(seconds, fps):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    frames = int(round((seconds % 1) * fps))
    return f"{hours:02d}:{minutes:02d}:{secs:02d}:{frames:02d}"

for i in range(len(clips_v1)):
    clip_v1 = clips_v1[i]

    # Check if there is a corresponding clip on Track 2 with the same index
    if i < len(clips_v2):
        clip_v2 = clips_v2[i]

        # Calculate clip duration (timeline duration in frames)
        duration_v1 = clip_v1.GetEnd() - clip_v1.GetStart()
        duration_v2 = clip_v2.GetEnd() - clip_v2.GetStart()

        # If durations match, copy name and metadata
        if duration_v1 == duration_v2:

            # Read name from Track 2
            name_v2 = clip_v2.GetName()

            # Set timeline clip name on Track 1
            clip_v1.SetName(name_v2)

            # Access MediaPoolItem and write metadata
            mp_item = clip_v1.GetMediaPoolItem()
            if mp_item:
                # Camera Notes
                mp_item.SetMetadata("Camera Notes", name_v2)

                # Copy Source Start TC from Track 2 as visible reference
                source_seconds = clip_v2.GetSourceStartTime()
                if source_seconds is not None:
                    tc = seconds_to_tc(source_seconds, fps)
                    mp_item.SetMetadata("Audio Start TC", tc)

                print(f"Clip {i+1}: OK → '{name_v2}' + Source TC {tc} copied")
            else:
                print(f"Clip {i+1}: No MediaPoolItem → only timeline name set")

        else:
            # Durations do not match → likely filler segment from NLE
            clip_v1.SetClipColor("Orange")
            print(f"Clip {i+1}: Duration mismatch → marked ORANGE")

    else:
        # No corresponding clip on Track 2
        clip_v1.SetClipColor("Orange")
        print(f"Clip {i+1}: No matching clip → marked ORANGE")

print("\nProcess completed ✅")