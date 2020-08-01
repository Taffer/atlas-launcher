# Atlas Launcher

Portable MMO downloader/launcher using manifests.

Atlas uses an XML-based manifest to download the files associated with an MMO:

* Downloads any files you don't already have.
* Checks existing files against provided digests; downloads any changed or
  corrupted files.
* Launches based one one of the included profiles.

The goals of Atlas are:

* Portable (Linux, MacOS, Windows, possibly others).
* Threaded design to lessen the impact of slow downloads.
* Able to recover from partial downloads.
* Smart about not reading/hashing files that haven't changed since the last
  check.

Atlas is named after Atlas Park, one of the starting zones in my favourite
MMO of all time, _City of Heroes_.

![Atlas Park splash screen](Splash_AtlasPark.jpg)

(Image courtesy of
[Paragon Wiki](https://archive.paragonwiki.com/wiki/Main_Page). It was
actually used in-game while loading the Atlas Park zone.)

## Manifest Format

The manifest is an XML file with the following structure:

```xml
<?xml version="1.0" ?>
<manifest>
    <label>MMO Name</label>
    <profiles>
        <!-- Launch profiles; architecture defaults to x86 (32-bit). -->
        <launch exec="path/to/binary.exe" order="0" params="command line args"
            architecture="x64">Display Name</launch>
        ...
    </profiles>
    <filelist>
        <!-- MD5 is used only to detect file changes, not to ensure security. -->
        <file name="path/to/filename" size="num_bytes" md5="MD5 digest">
            <url>...</url>
            ...
        </file>
        ...
    </filelist>
    <launchers>
        <!-- Supported launchers, to check for new versions. -->
        <launcher id="name" size="num_bytes" md5="MD5 digest" version="version_string">
            <url>...</url>
            ...
        </launcher>
    </launchers>
    <forums>
        <!-- Display names/links to game forums. -->
        <forum name="Display Name" url="..." />
        ...
    </forums>
    <!-- URL to the game's main web page. -->
    <webpage>...</webpage>
    <!-- Web page to display inside the launcher during check/download. -->
    <poster_image url="..." />
</manifest>
```

This isn't the cleanest XML format, but it grew over time.

## License

This code is covered by the included [MIT license](LICENSE).
