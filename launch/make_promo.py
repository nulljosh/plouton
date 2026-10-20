#!/usr/bin/env python3
"""Talli's commercial: launch/talli-promo.mp4 (1920x1080), talli-promo.vtt and talli-promo-poster.jpg.

The house shape (Bookrank's and Turing's ads): a voice carries it, every cut lands on a sentence, type cards
hold the few words, the real app plays in a phone frame, and it ends on the mark. The look is the landing
page's: grainy Talli-blue bands with public domain sculpture dithered into the band colours, thin system type.

1. Voice: one ElevenLabs line per shot (cached by turing/app/voice.py, so a rerun costs nothing).
2. App: launch/record.mjs records the real dashboard at phone size against a local demo server.
3. Stage: launch/stage.html plays the cut with that recording inside the phone; record.mjs records it at 1080p.
4. Mix: the voice on each cut, an original music bed ducked under it, loudness normalised.

Run from the repo root: ~/Documents/Code/turing/.venv/bin/python launch/make_promo.py
Needs ELEVENLABS_API_KEY (environment or the fish secrets file), ffmpeg, node and Google Chrome."""
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

APP_PORT, STAGE_PORT = 3123, 3124
DEMO_PASSWORD = "promo-demo"
VO_IN = 0.35  # the cut lands, the voice comes in a breath later

# One shot per sentence. `say` is spoken (spelled "Tally" so it is said right), `lines` are on screen.
SHOTS = [
    dict(kind="card", art="niche.png", lines=["Payday."], say="Payday shouldn't be a guessing game.", min=3.0),
    dict(kind="card", art="chiaroscuro.png", lines=["When does", "it land?", "How much?"], say="When does it land? How much is it?", min=3.0),
    dict(kind="phone", action="home", art="eirene.png", label="Home", lines=["One number.", "One date."],
         say="Tally puts it on one screen. The amount, and the day it lands.", min=4.6),
    dict(kind="phone", action="messages", art="chariot.png", label="Messages", lines=["Every letter.", "One list."],
         say="Every letter from the ministry, in one clean list.", min=4.2),
    dict(kind="phone", action="status", art="bronze.png", label="Status", lines=["Every benefit,", "one place."],
         say="Your assistance, your disability benefit and your tax credit, all in one place.", min=4.8),
    dict(kind="card", art="eirene.png", lines=["Free.", "Private.", "Yours."], say="Free. Private. Yours.", min=3.0),
    dict(kind="end", art="niche.png", say="Tally. Free on the App Store, and at tally dot jaybulb dot com.", min=5.6),
]
CAPTIONS = ["Payday shouldn't be a guessing game.", "When does it land? How much is it?",
            "Talli puts it on one screen. The amount, and the day it lands.", "Every letter from the ministry, in one clean list.",
            "Your assistance, your disability benefit and your tax credit, all in one place.", "Free. Private. Yours.",
            "Talli. Free on the App Store, and at talli.jaybulb.com"]


def clock(t):
    """Seconds as a WebVTT timestamp."""
    return f"{int(t // 60):02d}:{t % 60:06.3f}"


def duration(path):
    """Length of a media file in seconds."""
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def narrate(key):
    """One mp3 per shot; exits plainly if ElevenLabs gives nothing back."""
    clips = []
    for shot in SHOTS:
        mp3 = voice.eleven_mp3(shot["say"], key)
        if not mp3:
            sys.exit("ElevenLabs did not return audio for: " + shot["say"])
        clips.append((mp3, duration(mp3)))
    return clips


def record(args):
    """Run launch/record.mjs and return its JSON."""
    subprocess.run(["node", os.path.join(REPO, "launch", "record.mjs"), *args], capture_output=True, text=True, check=True)
    out_dir = args[3] if args[0] == "app" else args[2]
    with open(os.path.join(out_dir, "rec.json")) as f:
        return json.load(f)


def frames_to_video(rec, t0, out_dir, name, size):
    """Rebuild real time from stamped screencast frames (each holds until the next lands), from t0 to the end."""
    frames, end = rec["frames"], rec["end"]
    before = [f for f in frames if f[0] < t0]
    keep = ([[t0, before[-1][1]]] if before else []) + [f for f in frames if f[0] >= t0]
    lst = os.path.join(out_dir, name + ".txt")
    with open(lst, "w") as fh:
        for (ts, path), nxt in zip(keep, keep[1:] + [[end, None]]):
            fh.write(f"file '{path}'\nduration {max(0.001, nxt[0] - ts):.3f}\n")
        fh.write(f"file '{keep[-1][1]}'\n")
    mp4 = os.path.join(out_dir, name + ".mp4")
    ff("-f", "concat", "-safe", "0", "-i", lst, "-vf", f"scale={size},tpad=stop_mode=clone:stop_duration=3,fps=30,format=yuv420p",
       "-c:v", "libx264", "-crf", "18", "-g", "15", "-preset", "medium", "-t", f"{end - t0 + 2:.2f}", mp4)
    return mp4


def music(seconds, end_at, path, rate=44100):
    """An original, sample-free bed in D at 100 bpm: a soft string pad, warm piano plucks, a felt kick from bar
    two, a bell each bar, and one held chord under the end card. Mono wav, mixed under the voice."""
    import numpy as np
    n = int(seconds * rate)
    out = np.zeros(n)
    beat = 60 / 100
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)  # noqa: E731
    prog = [([62, 66, 69, 74], 38), ([61, 64, 69, 73], 33), ([59, 62, 66, 71], 35), ([59, 62, 67, 71], 31)]  # D A Bm G
    tune = [78, 76, 74, 76, 73, 71, 73, 76]

    def put(start, sig, gain=1.0):
        i = int(start * rate)
        if 0 <= i < n:
            m = min(len(sig), n - i)
            out[i:i + m] += gain * sig[:m]

    def t_(d):
        return np.arange(int(d * rate)) / rate

    def piano(m, d=1.6):
        x, f = t_(d), hz(m)
        return (np.sin(2 * np.pi * f * x) + 0.35 * np.sin(4 * np.pi * f * x) * np.exp(-x * 5) + 0.12 * np.sin(6 * np.pi * f * x) * np.exp(-x * 9)) \
            * np.exp(-x * 2.6) * np.minimum(1, x / 0.004)

    def pad(notes, d):
        x = t_(d)
        env = np.minimum(1, x / 1.2) * np.minimum(1, np.maximum(0, d - x) / 1.2)
        return sum(np.sin(2 * np.pi * hz(m) * (1 + det) * x) for m in notes for det in (-0.003, 0, 0.003)) / (3 * len(notes)) * env

    bar = beat * 4
    for b in range(int(end_at / bar) + 1):
        t0 = b * bar
        notes, root = prog[b % 4]
        put(t0, pad(notes, bar + 0.6), 0.32)
        put(t0, piano(root, bar), 0.45)
        for k in range(4):  # plucked chord tones on the beat, the tune on the off-beats from bar three
            if t0 + k * beat < end_at:
                put(t0 + k * beat, piano(notes[(k + 1) % 4]), 0.16)
                if b >= 2:
                    put(t0 + k * beat + beat / 2, piano(tune[(b * 2 + k) % 8], 1.2), 0.12)
        if 1 <= b and t0 < end_at:
            for k in range(4):
                x = t_(0.18)
                put(t0 + k * beat, np.sin(2 * np.pi * (46 + 60 * np.exp(-x * 35)) * x) * np.exp(-x * 18), 0.42 if k in (0, 2) else 0.22)
        put(t0, piano(notes[3] + 12, 2.0), 0.05)
    for m in (50, 62, 66, 69, 74, 78):  # the end card's chord, held
        put(end_at, piano(m, seconds - end_at), 0.16)
    put(end_at, pad([62, 66, 69, 74], seconds - end_at), 0.3)
    out *= 0.9 / max(1e-6, np.max(np.abs(out)))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype("<i2").tobytes())
    return path


def main():
    key = voice.eleven_key()
    if not key:
        sys.exit("No ELEVENLABS_API_KEY in the environment or the fish secrets file.")
    work = tempfile.mkdtemp()
    clips = narrate(key)
    durs = [max(s["min"], c[1] + VO_IN + 0.6) for s, c in zip(SHOTS, clips)]

    # 2. the app, for the phone shots, each held as long as its shot
    app_dir = os.path.join(work, "app")
    os.makedirs(app_dir)
    phone = [i for i, s in enumerate(SHOTS) if s["kind"] == "phone"]
    server = subprocess.Popen(["node", "src/api.js"], cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              env={**os.environ, "PORT": str(APP_PORT), "DEMO_PASSWORD": DEMO_PASSWORD, "CORS_ORIGINS": f"http://localhost:{APP_PORT}"})
    try:
        time.sleep(3)
        app = record(["app", f"http://localhost:{APP_PORT}", DEMO_PASSWORD, app_dir,
                      json.dumps([{"action": SHOTS[i]["action"], "hold": durs[i] + 0.5} for i in phone])])
    finally:
        server.terminate()
    t_app = app["starts"][0]
    stage_dir = os.path.join(work, "stage")
    os.makedirs(os.path.join(stage_dir, "art"))
    frames_to_video(app, t_app, app_dir, "screen", "1080:1920:flags=lanczos")
    shutil.copy(os.path.join(app_dir, "screen.mp4"), stage_dir)

    # 3. the stage, played once and recorded at 1080p
    shutil.copy(os.path.join(REPO, "launch", "stage.html"), stage_dir)
    shutil.copy(os.path.join(REPO, "web", "icon.svg"), stage_dir)
    for s in SHOTS:
        shutil.copy(os.path.join(REPO, "web", "art", s["art"]), os.path.join(stage_dir, "art"))
    plan = []
    for i, s in enumerate(SHOTS):
        p = {k: s[k] for k in ("kind", "art", "lines", "label", "center") if k in s}
        p["dur"] = durs[i]
        if s["kind"] == "phone":
            p["at"] = app["starts"][phone.index(i)] - t_app
        plan.append(p)
    http = subprocess.Popen([sys.executable, "-m", "http.server", str(STAGE_PORT), "--directory", stage_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(1)
        rec_dir = os.path.join(work, "rec")
        os.makedirs(rec_dir)
        stage = record(["stage", f"http://localhost:{STAGE_PORT}/stage.html", rec_dir, json.dumps(plan)])
    finally:
        http.terminate()
    picture = frames_to_video(stage, stage["starts"][0], rec_dir, "picture", "1920:1080")

    # 4. the mix: each line on its cut, the bed ducked under the voice
    cuts = [sum(durs[:i]) for i in range(len(durs))]
    total = sum(durs)
    bed = music(total, cuts[-1], os.path.join(work, "bed.wav"))
    inputs, filters = ["-i", picture, "-i", bed], []
    for i, ((mp3, _), at) in enumerate(zip(clips, cuts)):
        inputs += ["-i", mp3]
        ms = int((at + VO_IN) * 1000)
        filters.append(f"[{i + 2}:a]adelay={ms}|{ms}[a{i}]")
    mix = ("".join(f"[a{i}]" for i in range(len(clips))) + f"amix=inputs={len(clips)}:normalize=0,apad[v0];[v0]asplit=2[voice][vkey];"
           f"[1:a]volume=0.85,afade=t=in:d=0.4,afade=t=out:st={total - 2:.2f}:d=2[bed];"
           "[bed][vkey]sidechaincompress=threshold=0.025:ratio=6:attack=20:release=400[ducked];"
           "[voice][ducked]amix=inputs=2:normalize=0:duration=longest[m];[m]loudnorm=I=-16:TP=-1.5:LRA=11[aout];"
           f"[0:v]fade=t=in:d=0.4,fade=t=out:st={total - 0.6:.2f}:d=0.6,format=yuv420p[vout]")
    mp4 = os.path.join(work, "talli-promo.mp4")
    ff(*inputs, "-filter_complex", ";".join(filters + [mix]), "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.2f}",
       "-c:v", "libx264", "-crf", "23", "-maxrate", "6M", "-bufsize", "12M", "-tune", "grain", "-preset", "slow", "-r", "30", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", mp4)
    vtt = os.path.join(work, "talli-promo.vtt")
    with open(vtt, "w") as f:
        f.write("WEBVTT\n\n")
        for text, at, d in zip(CAPTIONS, cuts, durs):
            f.write(f"{clock(at + VO_IN)} --> {clock(at + d - 0.05)}\n{text}\n\n")
    poster = os.path.join(work, "talli-promo-poster.jpg")
    ff("-ss", f"{cuts[2] + 2.2:.2f}", "-i", mp4, "-frames:v", "1", "-q:v", "3", poster)
    for path in (mp4, vtt, poster):
        shutil.copy(path, os.path.join(REPO, "launch", os.path.basename(path)))
    print(json.dumps({"seconds": round(duration(mp4), 1), "mb": round(os.path.getsize(mp4) / 1e6, 2), "cuts": [round(c, 1) for c in cuts]}))


if __name__ == "__main__":
    main()
