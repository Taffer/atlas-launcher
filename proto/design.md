# Design Notes

Global config has: {
    "manifest_url": "game_dir",
    ...
    "last_manifest": "manifest_url",
    "last_profile": index,
    "md_threads": 2,  # Default, not exposed. Num MD5 threads.
    "dl_threads": 4,  # Default, not exposed. Num download threads.
}

For each known manifest, its URL. The last-used manifest is the default.

Cache file date/time/size/MD5; if date/time/size still match, and MD5 matches,
skip calculating the MD5 during verify, assume it's correct. Add a Force Verify
option that's off by default?

On startup, if we don't have manifest, prompt for manifest/game directory.
Otherwise, grab manifest, populate display, create threads, start checking
files. As files are not found or not validated, they're added to the DL queue.
The DL threads pick up work from the queue as it's available.

Progress bars are based on the total number of bytes reported by the manifest.
Maybe the bytes progress bar could be for the largest file currently
downloading/checking?

Advanced settings:

* WINE instance, otherwise get the one from `PATH`
* extra args
* extra environment variables

## GUI

```
Manifest: [drop-down]                                        {+}

================================================================
=========== (big rect for the <poster_image>) ==================
== Maybe we'll skip this for now? It PyWebkitGTK supported? ====
================================================================

Validating: [===progress bar for # of files===]
            [===progress bar for # of bytes===]

Downloading: [=== progress bar for # of files ===]
             [=== progress bar for # of bytes ===]

Profile: [drop-down]                             {Verify} {Play}
                                                   [x] Auto-play

[status line]
```

```
window:
    box - vertical, spacing=5:
        box - horizontal, spacing=5:
            label - "Manifest:"
            combobox? comboboxtext?
            button - "Add"
        HTML
        box - horizonal, spacing=5:
            label - "Validating"
            progress bar
        box - horizonal, spacing=5:
            label - "Downloading:"
            progress bar
        status line
```

## State Machine

Start
-> Display UI
   -> launch manifest loading thread
      -> loading
      -> error -> send Error state to UI
      -> success -> send Checking state to UI
      -> send Join Me to UI, exit thread
   -> no files? -> send DL state to UI w/all files, skip checking thread
   -> launch checking thread(s)
      -> file wrong? -> send DL state to UI w/that file
      -> file good? -> send Checked state to UI w/that file
      -> send Join Me to UI, exit thread
   -> launch DL thread(s)
      -> error -> send Error DL state to UI
      -> success -> send Done state to UI w/that file
      -> send Join Me to UI, exit thread

In a thread:
- get mutex
- if list has items, take thing from list, do thing
- release mutex
- if exit_thread flag set, send Join Me, exit
- else loop
