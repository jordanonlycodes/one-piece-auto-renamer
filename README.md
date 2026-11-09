
# One Piece Auto Renamer

A lightweight Python automation tool that monitors your Downloads folder, detects completed video downloads, renames One Piece episodes, and organizes them into a dedicated folder.

## Features

- Automatically monitors the Downloads directory.
- Detects completed video downloads.
- Waits until file sizes stabilize before processing.
- Extracts episode numbers from recognizable filenames.
- Renames episodes sequentially when no episode number is detected.
- Organizes episodes into a dedicated One Piece folder.
- Saves episode progress using JSON.
- Avoids overwriting existing episodes.

## Requirements

- Python 3.10 or newer
- Linux (tested on Arch Linux)
- No external Python dependencies.

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/one-piece-auto-renamer.git
cd one-piece-auto-renamer
```

## Usage

Run the script:

```bash
python auto_renamer.py
```

Press `Ctrl+C` to stop monitoring.

## Folder Structure

```text
Downloads/
├── One Piece/
│   ├── One Piece - Ep 914.mkv
│   ├── One Piece - Ep 915.mkv
│   └── One Piece - Ep 916.mkv
└── ...
```

## Configuration

The script has configurable settings for:

- Download directory
- Destination directory
- Starting episode number
- File stability duration
- Monitoring interval

## Limitations

- Episode detection depends on recognizable filenames.
- Downloads without identifiable episode numbers use the saved sequential counter.
- The script monitors video files directly inside the Downloads directory.
- It is designed for one active episode sequence at a time.

## License

MIT License
