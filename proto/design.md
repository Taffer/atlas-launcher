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

On startup, if we don't have manifest, prompt for manifest/game directory.
Otherwise, grab manifest, populate display, create threads, start checking
files. As files are not found or not validated, they're added to the DL queue.
The DL threads pick up work from the queue as it's available.

Progress bars are based on the total number of bytes reported by the manifest.

## GUI

```
Manifest: [drop-down]                                        {+}

================================================================
=========== (big rect for the <poster_image>) ==================
================================================================

Validating: [===progress bar===]
Downloading: [=== progress bar ===]

Profile: [drop-down]                             {Verify} {Play}

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
