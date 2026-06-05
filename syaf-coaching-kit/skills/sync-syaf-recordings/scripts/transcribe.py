#!/usr/bin/env python3
"""
transcribe.py — Upload a video/audio file to AssemblyAI with speaker diarization,
poll until complete, and write a JSON file the parent skill can read.

Uses curl for the upload step (the SDK's upload path has reliability issues with
larger files; plain HTTP works fine).

Usage:
    python3 transcribe.py <input_path> <output_json_path>

Reads API key from (in order):
    1. $ASSEMBLYAI_API_KEY environment variable
    2. ~/.assemblyai_api_key file
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path


API_BASE = "https://api.assemblyai.com/v2"


def load_api_key() -> str:
    key = os.environ.get("ASSEMBLYAI_API_KEY")
    if key:
        return key.strip()
    key_file = Path.home() / ".assemblyai_api_key"
    if key_file.exists():
        return key_file.read_text().strip()
    print(
        "ERROR: AssemblyAI API key not found. Set $ASSEMBLYAI_API_KEY or save the key to ~/.assemblyai_api_key.",
        file=sys.stderr,
    )
    sys.exit(3)


def maybe_recompress(file_path: Path) -> Path:
    """If audio is bigger than ~12 MB, re-encode to 24 kbps mono mp3 to fit under
    AssemblyAI's effective upload cap. ffmpeg required."""
    size_mb = file_path.stat().st_size / 1024 / 1024
    if size_mb <= 12:
        return file_path
    print(f"File is {size_mb:.1f} MB — re-encoding to 24 kbps mono mp3 to fit upload cap.", file=sys.stderr)
    out = file_path.with_suffix(".low.mp3")
    result = subprocess.run(
        ["ffmpeg", "-i", str(file_path), "-vn", "-ac", "1", "-ar", "16000", "-b:a", "24k", "-y", str(out)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not out.exists():
        print(f"ERROR: ffmpeg re-encode failed: {result.stderr[-500:]}", file=sys.stderr)
        sys.exit(8)
    print(f"Re-encoded to {out} ({out.stat().st_size//1024//1024} MB)", file=sys.stderr)
    return out


def upload_via_curl(file_path: Path, api_key: str) -> str:
    """Upload via curl. Returns the upload_url. Bypasses SDK upload (which is flaky)."""
    print(f"Uploading via curl: {file_path} ({file_path.stat().st_size // 1024 // 1024} MB)", file=sys.stderr)
    result = subprocess.run(
        [
            "curl",
            "--silent",
            "--show-error",
            "--max-time", "1800",  # 30 min
            "-X", "POST",
            f"{API_BASE}/upload",
            "-H", f"authorization: {api_key}",
            "-H", "content-type: application/octet-stream",
            "--data-binary", f"@{file_path}",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: curl upload failed: {result.stderr}", file=sys.stderr)
        sys.exit(5)
    try:
        body = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"ERROR: unexpected upload response: {result.stdout[:500]}", file=sys.stderr)
        sys.exit(5)
    upload_url = body.get("upload_url")
    if not upload_url:
        print(f"ERROR: no upload_url in response: {body}", file=sys.stderr)
        sys.exit(5)
    print(f"Upload complete. URL: {upload_url[:80]}...", file=sys.stderr)
    return upload_url


def request_transcript(upload_url: str, api_key: str) -> str:
    """POST /transcript. Returns transcript_id."""
    body = {
        "audio_url": upload_url,
        "speaker_labels": True,
        "speech_models": ["universal-2"],
    }
    req = urllib.request.Request(
        f"{API_BASE}/transcript",
        data=json.dumps(body).encode(),
        headers={"authorization": api_key, "content-type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"ERROR: transcript request failed: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode()[:500], file=sys.stderr)
        sys.exit(6)
    transcript_id = data.get("id")
    if not transcript_id:
        print(f"ERROR: no transcript id: {data}", file=sys.stderr)
        sys.exit(6)
    print(f"Transcript queued. ID: {transcript_id}", file=sys.stderr)
    return transcript_id


def poll_transcript(transcript_id: str, api_key: str) -> dict:
    """Poll until complete. Returns the full transcript object."""
    url = f"{API_BASE}/transcript/{transcript_id}"
    waited = 0
    while True:
        req = urllib.request.Request(url, headers={"authorization": api_key})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
        status = data.get("status")
        if status == "completed":
            print(f"Done after {waited}s.", file=sys.stderr)
            return data
        if status == "error":
            print(f"ERROR: AssemblyAI returned error: {data.get('error')}", file=sys.stderr)
            sys.exit(7)
        # queued / processing
        sleep_s = 5 if waited < 60 else 15
        print(f"Status: {status} (waited {waited}s, next check in {sleep_s}s)", file=sys.stderr)
        time.sleep(sleep_s)
        waited += sleep_s


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python3 transcribe.py <input_path> <output_json_path>", file=sys.stderr)
        sys.exit(1)

    input_path = Path(sys.argv[1]).expanduser().resolve()
    output_path = Path(sys.argv[2]).expanduser().resolve()

    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    api_key = load_api_key()
    upload_path = maybe_recompress(input_path)
    upload_url = upload_via_curl(upload_path, api_key)
    transcript_id = request_transcript(upload_url, api_key)
    transcript = poll_transcript(transcript_id, api_key)

    utterances = []
    for u in transcript.get("utterances") or []:
        utterances.append({
            "speaker": u.get("speaker"),
            "start_ms": u.get("start"),
            "end_ms": u.get("end"),
            "text": u.get("text"),
            "confidence": u.get("confidence"),
        })

    payload = {
        "transcript_id": transcript_id,
        "status": transcript.get("status"),
        "audio_duration_sec": transcript.get("audio_duration"),
        "speaker_count": len({u["speaker"] for u in utterances}) if utterances else 0,
        "utterance_count": len(utterances),
        "utterances": utterances,
        "full_text": transcript.get("text") or "",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(
        f"Done. {len(utterances)} utterances across {payload['speaker_count']} speakers.",
        file=sys.stderr,
    )
    print(f"Output: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
