#!/usr/bin/env python3
"""Talli's commercial: launch/talli-promo.mp4 (1080x1920), talli-promo.vtt and talli-promo-poster.jpg.

Records the real dashboard at phone size against a local demo server, voices each beat with ElevenLabs,
lays an original music bed under it (ducked under the voice) and ends on a card with the App Store line
and the site. Same recipe as turing/scripts/make_promo.py.

Run from the repo root: ~/Documents/Code/turing/.venv/bin/python launch/make_promo.py
Needs ELEVENLABS_API_KEY (environment or the fish secrets file), ffmpeg, and that venv's playwright + numpy.
Voice lines are cached by turing/app/voice.py, so a rerun costs nothing."""
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import wave

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/Documents/Code/turing/app"))
import voice  # noqa: E402

PORT = 3123
BASE = f"http://localhost:{PORT}"
VW, VH = 432, 768          # a phone's CSS width, 9:16
W, H = 1080, 1920
DEMO_PASSWORD = "promo-demo"

# (what is said, what the caption shows, what happens on screen). Spelled "Tally" so the voice says it right.
SEGMENTS = [
    ("Payday shouldn't be a guessing game.", "Payday shouldn't be a guessing game.", "home"),
    ("Tally shows your next cheque, and the day it lands.", "Talli shows your next cheque, and the day it lands.", "hide"),
    ("Every letter from the ministry, in one clean list.", "Every letter from the ministry, in one clean list.", "messages"),
    ("Your benefits, all in one place.", "Your benefits, all in one place.", "status"),
    ("Tally. Free on the App Store. Tally dot jaybulb dot com.", "Talli. Free on the App Store. talli.jaybulb.com", "card"),
]
HOLD = [4.2, 4.6, 4.6, 4.4, 6.0]  # the least each beat stays on screen

END_CARD = """(() => { const d = document.createElement('div');
  d.style.cssText = 'position:fixed;inset:0;z-index:999;background:#2F6FB0;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;font-family:-apple-system,BlinkMacSystemFont,Helvetica,sans-serif;text-align:center;opacity:0;transition:opacity .6s ease';
  d.innerHTML = '<img src="/icon.svg" width="96" height="96" style="border-radius:22%;box-shadow:0 8px 32px rgba(0,0,0,.25)">'
    + '<div style="font-size:44px;font-weight:200;letter-spacing:.2em;margin-top:8px">TALLI</div>'
    + '<div style="font-size:15px;letter-spacing:.14em;text-transform:uppercase;opacity:.85">BC disability assistance, counted</div>'
    + '<div style="margin-top:24px;height:48px;padding:0 24px;border-radius:999px;background:#fff;color:#2F6FB0;display:flex;align-items:center;font-size:17px;font-weight:600">Free on the App Store</div>'
    + '<div style="font-size:20px;font-weight:500;margin-top:8px">talli.jaybulb.com</div>';
  document.body.appendChild(d); requestAnimationFrame(() => requestAnimationFrame(() => { d.style.opacity = 1; })); })()"""


def clock(t):
    """Seconds as a WebVTT timestamp."""
    return f"{int(t // 60):02d}:{t % 60:06.3f}"


def duration(path):
    """Length of a media file in seconds."""
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def narrate(key):
    """One mp3 per beat; exits plainly if ElevenLabs gives nothing back."""
    clips = []
    for said, _, _ in SEGMENTS:
        mp3 = voice.eleven_mp3(said, key)
        if not mp3:
            sys.exit("ElevenLabs did not return audio for: " + said)
        clips.append((mp3, duration(mp3)))
    return clips


def button(page, label):
    """Click the first button whose text starts with label."""
    page.evaluate("(l) => [...document.querySelectorAll('button')].find(b => b.textContent.trim().startsWith(l)).click()", label)


def record(clips, out_dir):
    """launch/record.mjs drives Chrome through every beat and saves its screencast frames (1080x1920) with arrival times.
    Returns (ffmpeg concat list, [beat start seconds from the first beat])."""
    beats = [{"action": action, "hold": max(seconds + 0.6, HOLD[i]), "card": END_CARD}
             for i, ((_, seconds), (_, _, action)) in enumerate(zip(clips, SEGMENTS))]
    out = subprocess.run(["node", os.path.join(REPO, "launch", "record.mjs"), BASE, DEMO_PASSWORD, out_dir, json.dumps(beats)],
                         capture_output=True, text=True, check=True).stdout
    rec = json.loads(out.strip().splitlines()[-1])
    t0, end, frames = rec["starts"][0], rec["end"], rec["frames"]
    before = [f for f in frames if f[0] < t0]
    keep = ([[t0, before[-1][1]]] if before else []) + [f for f in frames if f[0] >= t0]
    lst = os.path.join(out_dir, "frames.txt")
    with open(lst, "w") as fh:  # each frame holds until the next one lands
        for (ts, path), nxt in zip(keep, keep[1:] + [[end, None]]):
            fh.write(f"file '{path}'\nduration {max(0.001, nxt[0] - ts):.3f}\n")
        fh.write(f"file '{keep[-1][1]}'\n")
    return lst, [s - t0 for s in rec["starts"]]


def music(seconds, path, rate=44100):
    """An original, sample-free bed: warm plucks over D, A, Bm, G at 112 bpm, a soft kick and hats from bar two,
    a bell on each bar and a held chord under the end card. Mono wav, mixed under the voice."""
    import numpy as np
    n = int(seconds * rate)
    out = np.zeros(n)
    beat = 60 / 112
    chords = [(73.42, [293.66, 369.99, 440.0, 587.33]), (55.0, [277.18, 329.63, 440.0, 554.37]),
              (61.74, [293.66, 369.99, 493.88, 587.33]), (49.0, [293.66, 392.0, 493.88, 587.33])]
    pattern = [0, 2, 1, 3, 2, 1, 3, 2]

    def put(start, sig):
        i = int(start * rate)
        if 0 <= i < n:
            m = min(len(sig), n - i)
            out[i:i + m] += sig[:m]

    def tone(f, dur, decay, harm=(1, 0.45, 0.2)):
        x = np.arange(int(dur * rate)) / rate
        return sum(h * np.sin(2 * np.pi * f * (k + 1) * x) for k, h in enumerate(harm)) * np.exp(-x * decay) * np.minimum(1, x / 0.004)

    end = max(0, seconds - 6.0)
    for bar in range(int(seconds / (beat * 4)) + 1):
        t0 = bar * beat * 4
        if t0 >= end:
            break
        root, notes = chords[bar % 4]
        for k, i in enumerate(pattern):
            put(t0 + k * beat / 2, 0.28 * tone(notes[i], 0.55, 8))
        put(t0, 0.5 * tone(root * 2, beat * 2, 2.2, (1, 0.25)))
        put(t0 + beat * 2, 0.38 * tone(root * 2, beat * 2, 2.2, (1, 0.25)))
        put(t0, 0.09 * tone(notes[3] * 2, 1.4, 2.6, (1, 0.3)))
        if bar >= 1:
            for b in range(4):
                x = np.arange(int(0.16 * rate)) / rate
                put(t0 + b * beat, 0.5 * np.sin(2 * np.pi * (48 + 70 * np.exp(-x * 40)) * x) * np.exp(-x * 20))
                rng = np.random.default_rng(bar * 4 + b)
                y = np.arange(int(0.04 * rate)) / rate
                put(t0 + b * beat + beat / 2, 0.07 * rng.standard_normal(len(y)) * np.exp(-y * 90))
    for f in (293.66, 369.99, 440.0, 587.33, 146.83):  # the end card's chord, held
        put(end, 0.26 * tone(f, 5.8, 0.9))
    out *= 0.9 / max(1e-6, np.max(np.abs(out)))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype("<i2").tobytes())
    return path


def build(webm, starts, clips, out_dir):
    """Voice delayed to each beat, the bed ducked under it, loudness normalised; plus captions and a poster."""
    total = starts[-1] + max(clips[-1][1], HOLD[-1]) + 1.2
    lead = 0.0
    bed = music(total, os.path.join(out_dir, "bed.wav"))
    inputs, filters = ["-f", "concat", "-safe", "0", "-i", webm, "-i", bed], []
    for i, ((mp3, _), start) in enumerate(zip(clips, starts)):
        inputs += ["-i", mp3]
        ms = int((start - lead) * 1000) + 250
        filters.append(f"[{i + 2}:a]adelay={ms}|{ms}[a{i}]")
    mix = ("".join(f"[a{i}]" for i in range(len(clips))) + f"amix=inputs={len(clips)}:normalize=0,apad[v0];[v0]asplit=2[voice][vkey];"
           f"[1:a]volume=0.8,afade=t=in:d=0.6,afade=t=out:st={total - lead - 2.5:.2f}:d=2.5[bed];"
           "[bed][vkey]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=450[ducked];"
           "[voice][ducked]amix=inputs=2:normalize=0:duration=longest[m];[m]loudnorm=I=-16:TP=-1.5:LRA=11[aout];"
           "[0:v]scale=1080:1920:flags=lanczos,tpad=stop_mode=clone:stop_duration=10,fps=30,format=yuv420p[vout]")
    mp4 = os.path.join(out_dir, "talli-promo.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filters + [mix]), "-map", "[vout]", "-map", "[aout]",
                    "-t", f"{total - lead:.2f}", "-c:v", "libx264", "-crf", "24", "-preset", "slow", "-pix_fmt", "yuv420p", "-r", "30",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", mp4], check=True)
    vtt = os.path.join(out_dir, "talli-promo.vtt")
    rel = [s - lead + 0.25 for s in starts]
    ends = rel[1:] + [duration(mp4)]
    with open(vtt, "w") as f:
        f.write("WEBVTT\n\n")
        for (_, shown, _), s, e in zip(SEGMENTS, rel, ends):
            f.write(f"{clock(s)} --> {clock(e - 0.05)}\n{shown}\n\n")
    poster = os.path.join(out_dir, "talli-promo-poster.jpg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{rel[0] + 2.5:.2f}", "-i", mp4, "-frames:v", "1", "-q:v", "3", poster], check=True)
    return mp4, vtt, poster


def main():
    key = voice.eleven_key()
    if not key:
        sys.exit("No ELEVENLABS_API_KEY in the environment or the fish secrets file.")
    work = tempfile.mkdtemp()
    server = subprocess.Popen(["node", "src/api.js"], cwd=REPO, env={**os.environ, "PORT": str(PORT), "DEMO_PASSWORD": DEMO_PASSWORD,
                              "CORS_ORIGINS": BASE}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(3)
        clips = narrate(key)
        webm, starts = record(clips, work)
        mp4, vtt, poster = build(webm, starts, clips, work)
    finally:
        server.terminate()
    for path in (mp4, vtt, poster):
        shutil.copy(path, os.path.join(REPO, "launch", os.path.basename(path)))
    print(json.dumps({"seconds": round(duration(mp4), 1), "mb": round(os.path.getsize(mp4) / 1e6, 2), "beats": [round(s, 1) for s in starts]}))


if __name__ == "__main__":
    main()
