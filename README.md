# UmapToUE4
Extracts Fortnite POIs/buildings and decompiles them back into Unreal Engine 4.

This is a *highly modified* version of [Amrsatrio](https://github.com/Amrsatrio)'s **BlenderUmap** repository, found [here](https://github.com/Amrsatrio/BlenderUmap), which adds onto the script to export models, textures, or fully textured .FBX files of an entire POI!

# Prerequisities:
As Amrsatrio originally said, **64-Bit Java [Offline] is required, and 32-Bit Java WILL NOT WORK.** Download [here](https://www.java.com/en/download/manual.jsp).
Choose **Windows Offline (64-bit)**

**Blender:** Download from Blender.org [HERE](https://www.blender.org/download/) or on Steam [HERE](https://store.steampowered.com/app/365670/Blender/)

**PSK-PSA Import:** Download the latest version of this, then install it as a plugin in Blender. Download: [Blender PSK-PSA Importer](https://github.com/Befzz/blender3d_import_psk_psa)

**Unreal Engine 4 (Optional):** Obviously required if you wish to move models into UE4.

# Usage:
 - Extract the Source Code and open the main folder.
 - Open `config.json` and edit it according to your needs.
    ```{
          "_Documentation": "https://github.com/Strayfade/.UmapToUE4/README.md",
          "PaksDirectory": "C:\\Users\\epicp\\Downloads\\Modnite\\Modnite\\FortniteGame\\Content\\Paks",
          "UEVersion": "GAME_UE4_22",
          "EncryptionKeys": [
	        {
	           "Guid": "00000000000000000000000000000000",
	          "Key": "0xDA62D5DBF537499EF82351FC4751D2AFC82E35CAF19945BDD02E3C6BB9462491"
	        }
          ],
          "bReadMaterials": true,
          "bRunUModel": true,
          "UModelAdditionalArgs": "",
          "bDumpAssets": false,
          "ExportPackage": "/Game/Athena/Maps/POI/Athena_POI_Bridge_002.umap"
        } ```
  - Documentation:  A link to this README
  - PaksDirectory:  Path to the `FortniteGame/Content/Paks` Folder, which contains game content. Note that this has to have double-backslashes.
  - UEVersion:      The Version of UE4 which Fortnite is running on. This is the version which the Paks are built based on. For me, Season 6 was `GAME_UE4_22`, but I believe that Fortnite now could be at `GAME_UE4_25` or `GAME_UE4_26`.
  - EncryptionKeys: Leave `GUID` header blank (zeroes), then input the Fortnite AES Key in the `Key` header. If you are using Fortnite 14.30 or below, your key can be found here: https://pastebin.com/raw/SCWdTWbj. If you are using a version after 14.30, your key can be found here: https://benbotfn.tk/api/v1/aes (what you're looking for is the `MainKey`).
  - bReadMaterials: Set this to true if you want textured meshes. It is true by default, so you should probably just skip over it.
  - bRunUmodel:     Exports Meshes and Textures using [Gildor](https://github.com/gildor2)'s [UE Viewer](https://github.com/gildor2/UEViewer), or Umodel. Generally good practice.
  - UModelAdditionalArgs: Adds extra command line arguments for Umodel. If you don't know what you're doing, leave it blank.
  - bDumpAssets:    Dumps Assets
  - ExportPackage:  **IMPORTANT: **This is the .UMAP file directory INSIDE OF THE GAME FILES.
  
1. Open UModel.exe

2. For the Path, input the PaksDirectory path from `config.json`. You will be asked for an AES key. This is the same Key from the `config.json` file.

3. Navigate to a .umap file you wish to move into either Blender or UE4

4. Right click on the .umap file in Umodel, then press "Copy Package Path". Paste this in the `ExportPackage` Header inside of `config.json`.

5. Run `BlenderUmap.bat`. Once it finishes, you will be given a line named "data_dir". Copy this entire line, and then close BlenderUmap.bat

6. Open Blender and navigate to the Scripting tab at the top.

7. Open `umap.py` from UmapToUE4 in the text editor in Blender.

![](https://i.imgur.com/pkP4wi1.png)

8. Paste your `data_dir` line into the same line in `umap.py`, replacing the existing variable. If you lost it, don't worry. To restart, just delete `processed.json` and start from step 5. ![](https://i.imgur.com/eT4vGEk.png)

9. Edit the options at the top of `umap.py` to fit your needs.

10. Press the Play button, or press `ALT+P` to run the script. Your model should appear in Blender, and you can view the textured model by pressing the third view-mode button, located Here:

![](https://i.imgur.com/7pomgPV.png)
