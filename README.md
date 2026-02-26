# 🎬 BANCAMP STUDIO V4 - Lyrics Video Creator

**THREE.JS EDITION** - Create stunning lyric videos with insane 3D visualizations!

![Status](https://img.shields.io/badge/status-PRODUCTION_READY-00ff00?style=for-the-badge)
![Docker](https://img.shields.io/badge/docker-READY-2496ED?style=for-the-badge&logo=docker)
![Three.js](https://img.shields.io/badge/three.js-r160-000000?style=for-the-badge&logo=three.js)

## 🔥 Features

### 12 Mind-Blowing Visualizations

All visualizations are **audio-reactive** and built with **Three.js**:

1. **🌟 PARTICLES 3D** - 5000 particles dancing to your music
2. **🌊 WAVEFORM 3D** - 32 colorful audio bars in 3D space
3. **🔮 AUDIO SPHERE** - Pulsating icosahedron with glow effects
4. **🕳️ TUNNEL VISION** - Infinite tunnel of rotating rings
5. **🌌 GALAXY SPIRAL** - 10,000 particles forming a spiral galaxy
6. **🎲 CUBE MATRIX** - 64 cubes in a reactive grid
7. **⚡ PLASMA FIELD** - 3000 particles in circular plasma motion
8. **🧬 DNA HELIX** - Double helix structure reacting to bass
9. **🌀 VORTEX SPIN** - Spiral lines forming a vortex
10. **📊 3D GRID PULSE** - Wave-like grid with audio peaks
11. **💫 ORBITAL RINGS** - 5 rings orbiting in different axes
12. **☁️ NEBULA CLOUD** - 8000 particles forming a nebula

### Other Features

- ✨ **Glitch Font Lyrics** - Uses [Rubik Glitch](https://fonts.google.com/specimen/Rubik+Glitch) for cyberpunk aesthetics
- 🎵 **LRC Support** - Timestamped lyrics with precision timing
- 🎬 **Multiple Frame Rates** - 24, 30, or 60 FPS
- 📦 **Batch Processing** - Efficient frame upload with concurrency
- 🐳 **Docker Ready** - One command to run
- 🔥 **Native FFmpeg** - Server-side video compilation
- 💚 **FastAPI Backend** - High-performance Python backend

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Modern web browser (Chrome/Firefox recommended)

### Installation

```bash
# Clone the repo
git clone https://github.com/khannover/lyrics-video-creator.git
cd lyrics-video-creator

# Build and run with Docker
docker build -t bancamp-studio .
docker run -p 3333:3333 -v $(pwd)/renders:/app/renders bancamp-studio
```

### Or use Docker Compose

```bash
docker-compose up
```

Then open: **http://localhost:3333/render.html**

## 📖 Usage

1. **Upload Audio** - Select your .mp3 or .wav file
2. **Upload Lyrics** - (Optional) Select your .lrc file with timestamped lyrics
3. **Choose Visualization** - Pick from 12 insane 3D effects
4. **Configure Settings** - Set batch size and frame rate
5. **Render** - Click "START COMPILATION" and watch the magic happen
6. **Download** - Your video will auto-download when ready!

### LRC Format Example

```lrc
[00:12.50]Welcome to the show
[00:15.80]This is how we roll
[00:19.20]Feel the bass drop low
[00:22.60]Watch the visuals glow
```

You can create .lrc files using tools like:
- [LRC Editor Online](https://lrc-maker.github.io/)
- [LRC Generator](https://www.lyrics.com/)

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Browser (render.html)           │
│  ┌───────────────────────────────────┐  │
│  │  Three.js Rendering Engine        │  │
│  │  - 12 Visualizers                 │  │
│  │  - Web Audio API                  │  │
│  │  - Canvas 2D (lyrics overlay)     │  │
│  └───────────────────────────────────┘  │
└───────────────┬─────────────────────────┘
                │ REST API (FastAPI)
┌───────────────▼─────────────────────────┐
│         Python Backend (server.py)       │
│  ┌───────────────────────────────────┐  │
│  │  Session Management               │  │
│  │  Frame Storage                    │  │
│  │  FFmpeg Video Compilation         │  │
│  └───────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## 🎨 Customization

### Adding New Visualizers

1. Create a new class in `render.html`:

```javascript
class MyCustomVisualizer {
    constructor() {
        // Initialize Three.js objects
    }
    
    update(audioData, frame) {
        // Update based on audio
    }
    
    destroy() {
        // Cleanup
    }
}
```

2. Add to the visualizers object:

```javascript
const visualizers = {
    // ... existing visualizers
    mycustom: MyCustomVisualizer
};
```

3. Add to the select dropdown:

```html
<option value="mycustom">MY CUSTOM VIZ 🚀</option>
```

## 🔧 API Endpoints

### POST `/api/start`
Create a new render session.

**Response:**
```json
{
    "session_id": "abc12345"
}
```

### POST `/api/audio/{session_id}`
Upload audio file for the session.

### POST `/api/frame/{session_id}`
Upload a rendered frame.

**Form Data:**
- `frame_index`: Frame number
- `frame`: Image file (webp/jpg/png)

### POST `/api/compile/{session_id}`
Compile all frames + audio into final MP4.

**Form Data:**
- `fps`: Frame rate (24/30/60)

**Response:**
```json
{
    "status": "done",
    "download": "/api/download/abc12345"
}
```

### GET `/api/download/{session_id}`
Download the compiled video.

### DELETE `/api/cleanup/{session_id}`
Clean up session files.

## 🐛 Troubleshooting

### Video has no audio
- Check that FFmpeg has libmp3lame support: `ffmpeg -encoders | grep mp3`
- Ensure audio file is valid MP3 or WAV

### Frames not rendering
- Check browser console for errors
- Try reducing batch size
- Ensure sufficient disk space

### FFmpeg compilation fails
- Check logs: `docker logs <container_id>`
- Verify frame format matches (webp/jpg/png)
- Ensure frame sequence is complete

## 🎯 Performance Tips

1. **Batch Size**: Use 60 for balanced performance, 120 for faster uploads (if stable)
2. **Frame Rate**: 30 FPS is the sweet spot (720p@30fps = ~3MB/min)
3. **Visualizer**: Some visualizers are more GPU-intensive (Particles3D, Nebula)
4. **Browser**: Chrome/Edge perform better with Three.js than Firefox

## 📊 Technical Specs

- **Output Resolution**: 1280x720 (720p HD)
- **Video Codec**: H.264 (libx264, ultrafast preset)
- **Audio Codec**: MP3 (libmp3lame, 192kbps)
- **Frame Format**: WebP (quality 0.75) or JPG
- **Pixel Format**: yuv420p (maximum compatibility)

## 🤝 Contributing

Want to add more visualizers? PRs welcome!

1. Fork the repo
2. Create your feature branch
3. Add your visualizer class
4. Test it thoroughly
5. Submit a PR

## 📜 License

MIT License - do whatever the fuck you want with it!

## 🙏 Credits

- **Three.js** - The amazing 3D library
- **FastAPI** - Fast Python web framework
- **FFmpeg** - The king of video processing
- **Rubik Glitch Font** - Google Fonts

## 💬 Support

Having issues? Check:
1. Docker logs: `docker logs <container>`
2. Browser console (F12)
3. [Open an issue](https://github.com/khannover/lyrics-video-creator/issues)

---

**Made with 🔥 by [Kai Hannover](https://github.com/khannover)**

**Bancamp Artist?** Check out [bancamp.de](https://bancamp.de)
