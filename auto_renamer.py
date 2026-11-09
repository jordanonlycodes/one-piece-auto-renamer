
import json
import re
import time
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================

DOWNLOAD_DIR = Path.home() / "Downloads"
ONE_PIECE_DIR = DOWNLOAD_DIR / "One Piece"

STATE_FILE = Path(__file__).with_name("episode_state.json")

FIRST_EPISODE = 917
POLL_INTERVAL = 2
STABLE_SECONDS = 15

VIDEO_EXTENSIONS = {
    ".mkv", ".mp4", ".avi", ".mov",
    ".webm", ".m4v"
}

TEMP_SUFFIXES = (
    ".crdownload",
    ".part",
    ".tmp",
    ".download"
)

tracked_files = {}


# ==========================================
# EPISODE COUNTER
# ==========================================

def load_counter():

    if not STATE_FILE.exists():
        save_counter(FIRST_EPISODE)
        return FIRST_EPISODE

    try:
        data = json.loads(STATE_FILE.read_text())
        return max(FIRST_EPISODE, int(data["next_episode"]))

    except (ValueError, KeyError, OSError, TypeError):
        print("[WARNING] Invalid counter. Starting at 917.")
        save_counter(FIRST_EPISODE)
        return FIRST_EPISODE


def save_counter(number):

    temp_file = STATE_FILE.with_suffix(".tmp")

    temp_file.write_text(
        json.dumps({"next_episode": number}, indent=4)
    )

    temp_file.replace(STATE_FILE)


# ==========================================
# EPISODE NUMBER DETECTION
# ==========================================

def extract_episode_number(filename):

    name = Path(filename).stem

    patterns = [
        r"one[\s._-]*piece[\s._-]*(?:episode|ep)?[\s._-]*(\d{1,4})",
        r"(?:episode|ep)[\s._-]*(\d{1,4})",
        r"^(\d{1,4})$"
    ]

    for pattern in patterns:

        match = re.search(pattern, name, re.IGNORECASE)

        if match:
            return int(match.group(1))

    return None


# ==========================================
# FILE CHECKS
# ==========================================

def is_video(file):

    return file.suffix.lower() in VIDEO_EXTENSIONS


def is_temporary(file):

    return file.name.lower().endswith(TEMP_SUFFIXES)


def has_partial_download(file):

    return any(
        Path(str(file) + suffix).exists()
        for suffix in TEMP_SUFFIXES
    )


# ==========================================
# DESTINATION CHECK
# ==========================================

def destination_for(number, extension):

    return ONE_PIECE_DIR / (
        f"One Piece - Ep {number}{extension.lower()}"
    )


def episode_exists(number):

    return any(
        ONE_PIECE_DIR.glob(f"One Piece - Ep {number}.*")
    )


# ==========================================
# PROCESS COMPLETED EPISODE
# ==========================================

def process_episode(file, next_episode):

    detected_number = extract_episode_number(file.name)

    if detected_number is not None:
        episode_number = detected_number
    else:
        episode_number = next_episode

    destination = destination_for(
        episode_number,
        file.suffix
    )

    # Never overwrite existing episodes
    if episode_exists(episode_number):

        print(
            f"[CONFLICT] Episode {episode_number} "
            "already exists in One Piece folder."
        )

        print(f"[SKIPPED] {file.name}")

        return next_episode

    try:

        file.rename(destination)

        print("\n" + "=" * 45)
        print(f"[SUCCESS] Episode {episode_number}")
        print(f"[MOVED] {destination.name}")

        # Only advance when the expected episode arrives.
        # Higher episodes never jump the sequence.
        if episode_number == next_episode:

            next_episode += 1
            save_counter(next_episode)

        print(f"[NEXT EPISODE] {next_episode}")
        print("=" * 45)

        return next_episode

    except OSError as error:

        print(f"[ERROR] {file.name}: {error}")

        return next_episode


# ==========================================
# DOWNLOAD MONITOR
# ==========================================

def monitor_downloads():

    ONE_PIECE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    next_episode = load_counter()

    print("\n" + "=" * 50)
    print("          ONE PIECE AUTO-RENAMER")
    print("=" * 50)

    print(f"Monitoring: {DOWNLOAD_DIR}")
    print(f"Destination: {ONE_PIECE_DIR}")
    print(f"Next episode: {next_episode}")

    print("=" * 50)
    print("Waiting for downloads...")
    print("Press CTRL+C to stop.\n")

    while True:

        current_time = time.monotonic()

        ready_files = []

        for file in DOWNLOAD_DIR.iterdir():

            if not file.is_file():
                continue

            if not is_video(file):
                continue

            if is_temporary(file):
                continue

            try:
                current_size = file.stat().st_size

            except OSError:
                continue

            if current_size == 0:
                continue

            # First detection
            if file not in tracked_files:

                tracked_files[file] = {
                    "size": current_size,
                    "stable_since": current_time
                }

                print(f"[DETECTED] {file.name}")

                continue

            info = tracked_files[file]

            # File is still changing
            if current_size != info["size"]:

                info["size"] = current_size
                info["stable_since"] = current_time

                continue

            # Check stability
            stable_for = (
                current_time - info["stable_since"]
            )

            if stable_for >= STABLE_SECONDS:

                if not has_partial_download(file):
                    ready_files.append(file)

        # Process numbered episodes first
        ready_files.sort(
            key=lambda file: (
                extract_episode_number(file.name) is None,
                extract_episode_number(file.name) or 0
            )
        )

        for file in ready_files:

            if not file.exists():
                tracked_files.pop(file, None)
                continue

            next_episode = process_episode(
                file,
                next_episode
            )

            tracked_files.pop(file, None)

        time.sleep(POLL_INTERVAL)


# ==========================================
# START PROGRAM
# ==========================================

if __name__ == "__main__":

    try:

        monitor_downloads()

    except KeyboardInterrupt:

        print("\n[STOPPED] Auto-Renamer stopped.")
        print("[INFO] Episode counter saved.")
