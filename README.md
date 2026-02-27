# nle_mixdown_metadata_bridge

## Version
1.0.0

## Author
Sebastian Schmidt

## License
GNU General Public License v3.0 or later

---

# Description

`nle_mixdown_metadata_bridge` is a scripting utility for **DaVinci Resolve**.
It copies source clip names and source TC to a splitted mixdown, imported by Scene Cut Detection via EDL.

This is usefull for roundtrip workflows from NLE systems such as Avid Media Composer or Adobe Premiere Pro to DaVinci Resolve.
It combines the robustness of a fully baked mixdown with the metadata advantages of an EDL. Now you can identify source cameras in mixdowns.

# Workflow
1. Export a video mixdown and EDL from your NLE of your choice (it's recommendet to delete all EDL lines starting with `M2`)
2. Import the mixdown using the EDL within DaVinci's Scene Cut Detection
3. Create a new timeline with the imported mixdown clips on V1
4. Import the very same EDL via Timelines → Import, don't point to any media files
5. Copy the offline clips from the EDL import to V2 above the mixdown clips  
   Now you should have 2 Video Tracks with the same amount of clips and duration:  

   | Track                 |              |              |              | 
   |-----------------------|--------------|--------------|--------------|  
   | V2 (offline, EDL)     | Clip Alpha   | Clip Bravo   | Clip Charlie |  
   | V1 (splitted Mixdown) | Clip Mixdown | Clip Mixdown | Clip Mixdown |  

   
7. In the media pool make these columns visible: `Camera Notes`, `Audio Start TC`
8. Run the script `nle_mixdown_metadata_bridge`  
   Now you should see:
   
   | Track                 |              |              |              | 
   |-----------------------|--------------|--------------|--------------|  
   | V2 (offline, EDL)     | Clip Alpha   | Clip Bravo   | Clip Charlie |  
   | V1 (splitted Mixdown) | Clip Alpha   | Clip Bravo   | Clip Charlie |

# What the script does
The script copies `source clip names` from an imported offline EDL (Track V2) to `mixdown clip names` (Track V1)
and writes those names into the `Camera Notes` column in the Media Pool.
It also copies the EDL `Source Start TC` into the mixdown clips `Audio Start TC` for reference purposes.

Due to EDL limitations, the copied TC is only valid if the framerates of the EDL's source and record, and the DaVinci timeline, are identical. 

Clips with mismatched durations or missing counterparts (e.g., filler or gap segments from NLE exports) are not processed and are instead highlighted in **orange** on Track 1 for review.

---

# Installation

To make the script available in DaVinci Resolve, copy the file `nle_mixdown_metadata_bridge.py` into one of the following folders:

### Mac OS X:
      - All users: /Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts
      - Specific user:  /Users/<UserName>/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts
### Windows:
      - All users: %PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts
      - Specific user: %APPDATA%\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts
### Linux:
      - All users: /opt/resolve/Fusion/Scripts  (or /home/resolve/Fusion/Scripts/ depending on installation)
      - Specific user: $HOME/.local/share/DaVinciResolve/Fusion/Scripts

For further information, see **DaVinci Resolve → Help → Documentation → Developer**.

---


---

# Running the Script

## From the Workspace Menu
1. Start DaVinci Resolve.  
2. Open the menu `Workspace → Scripting`.  
3. Select the script `nle_mixdown_metadata_bridge.py` from the list.  
4. The script will run and:
   - Copy clip names from Track 2 to Track 1  
   - Copy clip names into the `Camera Notes` metadata field
   - Copy Source Start TC from Track 2 to Audio Start TC of the mixdown clips
   - Highlight any unmatched or duration-mismatched clips in orange

## Directly in the Resolve Console
If the script is not installed in the Scripting folders, you can run it directly from the DaVinci Resolve Python console:

1. Open the Console and switch to Python 3.  
2. Copy and paste the code starting from the line:

```python
# you can run the code below directly from the console. Switch Console to Python 3 before.
```

3. Press Enter to execute the script.  
4. The script will perform the same actions as described above.

---

# Notes

- The script assumes Track 1 and Track 2 are derived from the same EDL (CMX3600 or File_129) for best results.  
- Clips with differing durations (e.g., filler segments from Avid exports) are not renamed and are instead highlighted in orange for review.  
- Ensure Python 3 is installed and recognized by DaVinci Resolve for scripting.  

---

## Contact

For questions, feedback, or bug reports, please contact **Sebastian Schmidt** via email at `sebastian@phonvision.com` or via the GitHub repository: [https://github.com/Bastzonik/nle_mixdown_metadata_bridge](https://github.com/Bastzonik/nle_mixdown_metadata_bridge)

---

# License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but **WITHOUT ANY WARRANTY**; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details: <https://www.gnu.org/licenses/>.
