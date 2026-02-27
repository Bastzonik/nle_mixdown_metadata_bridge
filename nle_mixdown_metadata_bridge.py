# nle_mixdown_metadata_bridge.py
# Version: 1.0.0
# Author: Sebastian Schmidt
# License: GNU General Public License v3.0

"""
nle_mixdown_metadata_bridge.py

Copies clip names from an imported offline EDL (Track V2)
to scene-detected mixdown clips (Track V1)
and writes those names into the Camera Notes column in the Media Pool.

Also copies the EDL Source Start TC into the mixdown clips'
Audio Start TC field for reference purposes.

Clips with mismatched durations or missing counterparts
are highlighted in orange on Track 1.
"""

# -------------------------------------------------------------------
# Resolve Bootstrap (cross-platform, no external dependencies)
# -------------------------------------------------------------------

import sys
import os


def get_resolve():
    """
    Returns a Resolve scripting object.
    Works from Script Menu and external execution.
    """

    # 1. Running inside Resolve Console
    if "app" in globals():
        try:
            return app.GetResolve()
        except Exception:
            pass

    # 2. Standard import (if PYTHONPATH configured)
    try:
        import DaVinciResolveScript as bmd
        return bmd.scriptapp("Resolve")
    except ImportError:
        pass

    # 3. Fallback: default installation paths
    if sys.platform.startswith("darwin"):
        expected_path = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
    elif sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
        expected_path = os.path.join(
            os.getenv("PROGRAMDATA"),
            "Blackmagic Design",
            "DaVinci Resolve",
            "Support",
            "Developer",
            "Scripting",
            "Modules"
        )
    elif sys.platform.startswith("linux"):
        expected_path = "/opt/resolve/Developer/Scripting/Modules/"
    else:
        raise RuntimeError("Unsupported operating system")

    module_path = os.path.join(expected_path, "DaVinciResolveScript.py")

    if not os.path.exists(module_path):
        raise RuntimeError("DaVinciResolveScript.py not found.")

    import importlib.util
    spec = importlib.util.spec_from_file_location("DaVinciResolveScript", module_path)
    bmd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bmd)

    return bmd.scriptapp("Resolve")


# -------------------------------------------------------------------
# Connect to Resolve
# -------------------------------------------------------------------

resolve = get_resolve()

if not resolve:
    print("❌ Unable to connect to DaVinci Resolve.")
    sys.exit(1)

pm = resolve.GetProjectManager()
project = pm.GetCurrentProject()

if not project:
    print("❌ No active project.")
    sys.exit(1)

timeline = project.GetCurrentTimeline()

if not timeline:
    print("❌ No active timeline.")
    sys.exit(1)

print(f"✔ Project  : {project.GetName()}")
print(f"✔ Timeline : {timeline.GetName()}\n")

# -------------------------------------------------------------------
# Timeline Setup
# -------------------------------------------------------------------

fps = float(timeline.GetSetting("timelineFrameRate"))
print(f"Timeline framerate detected: {fps} fps\n")

track_v1 = 1
track_v2 = 2

clips_v1 = timeline.GetItemListInTrack("video", track_v1)
clips_v2 = timeline.GetItemListInTrack("video", track_v2)

if not clips_v1:
    print("❌ No clips found on Track V1.")
    sys.exit(1)

if not clips_v2:
    print("❌ No clips found on Track V2.")
    sys.exit(1)

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


# -------------------------------------------------------------------
# Processing
# -------------------------------------------------------------------

for i in range(len(clips_v1)):
    clip_v1 = clips_v1[i]

    if i < len(clips_v2):
        clip_v2 = clips_v2[i]

        duration_v1 = clip_v1.GetEnd() - clip_v1.GetStart()
        duration_v2 = clip_v2.GetEnd() - clip_v2.GetStart()

        if duration_v1 == duration_v2:

            name_v2 = clip_v2.GetName()
            clip_v1.SetName(name_v2)

            mp_item = clip_v1.GetMediaPoolItem()

            if mp_item:
                mp_item.SetMetadata("Camera Notes", name_v2)

                tc = None
                source_seconds = clip_v2.GetSourceStartTime()

                if source_seconds is not None:
                    tc = seconds_to_tc(source_seconds, fps)
                    mp_item.SetMetadata("Audio Start TC", tc)

                if tc:
                    print(f"Clip {i+1}: OK → '{name_v2}' + Source TC {tc} copied")
                else:
                    print(f"Clip {i+1}: OK → '{name_v2}' copied (no Source TC)")
            else:
                print(f"Clip {i+1}: No MediaPoolItem → only timeline name set")

        else:
            clip_v1.SetClipColor("Orange")
            print(f"Clip {i+1}: Duration mismatch → marked ORANGE")

    else:
        clip_v1.SetClipColor("Orange")
        print(f"Clip {i+1}: No matching clip → marked ORANGE")

print("\nProcess completed ✅")
