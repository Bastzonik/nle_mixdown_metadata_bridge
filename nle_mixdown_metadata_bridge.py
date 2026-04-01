# nle_mixdown_metadata_bridge.py
# Version: 1.2.0
# Author: Sebastian Schmidt
# License: GNU General Public License v3.0

"""
Version 1.2.0

NEW:
- Timeline-position based matching (no index matching anymore)
- Automatically ignores non-matching clips (e.g. graphics, bars, fillers)
- Robust against offsets and additional clips in V2

Copies clip names from an imported offline EDL (Track V2)
to scene-detected mixdown clips (Track V1)
and writes those names into the Shot column in the Media Pool.

Also copies the EDL Source Start TC into the mixdown clips'
Audio Start TC field for reference purposes.

Clips without a matching counterpart are highlighted in orange.
"""

# -------------------------------------------------------------------
# Resolve Bootstrap
# -------------------------------------------------------------------

import sys
import os

def get_resolve():
    if "app" in globals():
        try:
            return app.GetResolve()
        except:
            pass

    try:
        import DaVinciResolveScript as bmd
        return bmd.scriptapp("Resolve")
    except ImportError:
        pass

    if sys.platform.startswith("win"):
        expected_path = os.path.join(
            os.getenv("PROGRAMDATA"),
            "Blackmagic Design",
            "DaVinci Resolve",
            "Support",
            "Developer",
            "Scripting",
            "Modules"
        )
    elif sys.platform.startswith("darwin"):
        expected_path = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
    else:
        expected_path = "/opt/resolve/Developer/Scripting/Modules/"

    module_path = os.path.join(expected_path, "DaVinciResolveScript.py")

    import importlib.util
    spec = importlib.util.spec_from_file_location("DaVinciResolveScript", module_path)
    bmd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bmd)

    return bmd.scriptapp("Resolve")


# -------------------------------------------------------------------
# Connect
# -------------------------------------------------------------------

resolve = get_resolve()

pm = resolve.GetProjectManager()
project = pm.GetCurrentProject()
timeline = project.GetCurrentTimeline()

if not timeline:
    print("❌ No active timeline.")
    sys.exit()

print(f"✔ Timeline: {timeline.GetName()}")

fps = float(timeline.GetSetting("timelineFrameRate"))

# -------------------------------------------------------------------
# Tracks
# -------------------------------------------------------------------

track_v1 = 1
track_v2 = 2

clips_v1 = timeline.GetItemListInTrack("video", track_v1)
clips_v2 = timeline.GetItemListInTrack("video", track_v2)

# Sort by timeline position (CRITICAL)
clips_v1 = sorted(clips_v1, key=lambda c: c.GetStart())
clips_v2 = sorted(clips_v2, key=lambda c: c.GetStart())

print(f"Track V1: {len(clips_v1)} clips")
print(f"Track V2: {len(clips_v2)} clips\n")


# -------------------------------------------------------------------
# Helper
# -------------------------------------------------------------------

def seconds_to_tc(seconds, fps):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    frames = int(round((seconds % 1) * fps))
    return f"{hours:02d}:{minutes:02d}:{secs:02d}:{frames:02d}"


def find_matching_clip(v1_clip, v2_clips, tolerance=1):
    v1_start = v1_clip.GetStart()

    for c in v2_clips:
        if abs(c.GetStart() - v1_start) <= tolerance:
            return c

    return None


# -------------------------------------------------------------------
# Processing
# -------------------------------------------------------------------

for i, clip_v1 in enumerate(clips_v1):

    v1_start = clip_v1.GetStart()
    v1_end = clip_v1.GetEnd()

    clip_v2 = find_matching_clip(clip_v1, clips_v2)

    print(f"\n--- Clip {i+1} ---")
    print(f"V1 Start: {v1_start} | End: {v1_end}")

    if clip_v2:

        v2_start = clip_v2.GetStart()
        v2_end = clip_v2.GetEnd()

        duration_v1 = v1_end - v1_start
        duration_v2 = v2_end - v2_start

        print(f"V2 Start: {v2_start} | End: {v2_end}")
        print(f"Duration V1: {duration_v1} | V2: {duration_v2}")

        if duration_v1 == duration_v2:

            name_v2 = clip_v2.GetName()
            clip_v1.SetName(name_v2)

            mp_item = clip_v1.GetMediaPoolItem()

            if mp_item:
                mp_item.SetMetadata("Shot", name_v2)

                source_seconds = clip_v2.GetSourceStartTime()
                tc = None

                if source_seconds is not None:
                    tc = seconds_to_tc(source_seconds, fps)
                    mp_item.SetMetadata("Audio Start TC", tc)

                if tc:
                    print(f"✔ MATCH → '{name_v2}' + TC {tc}")
                else:
                    print(f"✔ MATCH → '{name_v2}' (no TC)")

        else:
            clip_v1.SetClipColor("Orange")
            print("❌ Duration mismatch → ORANGE")

    else:
        clip_v1.SetClipColor("Orange")
        print("❌ No matching V2 clip → ORANGE")


print("\nProcess completed ✅")
