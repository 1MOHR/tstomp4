# tstomp4
.ts to .mp4 converter for HDZero DVR footage.

---
This was designed for macOS and that's all it's tested on, however it's just python so it should work on others.
It uses pyqt6 for the UI and ffmpeg for the conversion. It's a glorified ffmpeg terminal command but I feel this is much nicer than opening the terminal every time I want to import DVR recordings. It could also be packed into a .app or .exe if you want.

Prerequisites:
- FFMPEG installed (I used homebrew)
- pyqt6 installed
