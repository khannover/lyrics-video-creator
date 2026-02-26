# ⚡ QUICKSTART GUIDE

**Get your lyric videos rendering in under 2 minutes!**

## Option 1: Docker (Recommended) 🐳

```bash
# Clone and run in one go
git clone https://github.com/khannover/lyrics-video-creator.git
cd lyrics-video-creator
docker-compose up
```

Then open: **http://localhost:3333/render.html**

## Option 2: Manual Setup 🔧

```bash
# Prerequisites: Python 3.11+, FFmpeg

# Clone repo
git clone https://github.com/khannover/lyrics-video-creator.git
cd lyrics-video-creator

# Install Python dependencies
pip install -r requirements.txt

# Run server
uvicorn server:app --host 0.0.0.0 --port 3333
```

Then open: **http://localhost:3333/render.html**

## First Render Test 🎬

1. **Get test files**:
   - Use any MP3 file you have
   - Use the included `example.lrc` or create your own

2. **In the web interface**:
   - Click "SOURCE_AUDIO" → select your MP3
   - Click "LYRICS_FILE" → select your .lrc file
   - Choose a visualization (try **PARTICLES 3D** first!)
   - Click **START COMPILATION**

3. **Wait for magic** ✨
   - Watch the progress bar
   - Preview updates in real-time
   - Video auto-downloads when done!

## Creating LRC Files 🎵

LRC format is simple:

```lrc
[MM:SS.xx]Lyric text here
[00:12.50]First line
[00:15.80]Second line
[00:19.20]Third line
```

**Tools to create LRC:**
- [LRC Maker](https://lrc-maker.github.io/) - Best online tool
- [MiniLyrics](http://www.crintsoft.com/) - Desktop app
- Or manually with any text editor!

## Pro Tips 🚀

1. **Start with 30 FPS** - Balanced speed and quality
2. **Use WebP format** - Smaller file sizes, faster uploads
3. **Batch size 60** - Good default for most systems
4. **Test short clips first** - Render 30 seconds before full song
5. **Modern browser** - Chrome/Edge work best

## Troubleshooting 🐛

**Video not rendering?**
- Check browser console (F12)
- Try different batch size
- Ensure enough disk space

**No audio in output?**
- Verify MP3 file is valid
- Check FFmpeg logs in Docker

**Slow rendering?**
- Lower FPS to 24
- Choose simpler visualizations
- Increase batch size to 120

## What's Next? 🎯

- Try all 12 visualizations!
- Experiment with different frame rates
- Create your own visualizer (see README.md)
- Share your creations on [Bancamp](https://bancamp.de)

## Need Help? 👋

- Check [README.md](README.md) for full docs
- Open an [issue](https://github.com/khannover/lyrics-video-creator/issues)
- Join discussions on GitHub

---

**Now go create some fucking amazing lyric videos! 🔥**
