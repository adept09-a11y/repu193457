# 💖 Neon Heart Animation - Desktop Application

A beautiful animated neon heart application for Windows with rainbow colors, glowing effects, particles, and romantic text.

## ✨ Features

- **Rainbow Neon Heart**: Smooth color cycling through all rainbow hues
- **Glow Effect**: Multi-layered glow simulation for realistic neon appearance
- **Particle System**: Sparkling particles that emanate from the heart
- **Pulsing Animation**: Gentle heartbeat-like pulsing after fade-in
- **Neon Text**: "люблю тебя, енечка" appears with glowing effect
- **Background Music**: Optional romantic background music
- **Restart Functionality**: Click or press any key to restart the animation

## 📋 Requirements

- Python 3.8 or higher
- pygame library
- PyInstaller (for building .exe)

## 🚀 Installation & Running

### 1. Install Dependencies

```bash
pip install pygame
```

### 2. Run the Application

```bash
python neon_heart_app.py
```

### 3. Controls

- **ESC**: Quit the application
- **Any other key** or **Mouse click**: Restart animation

## 🎵 Adding Background Music (Optional)

1. Create an `assets` folder in the same directory as the script:
   ```
   neon_heart_app.py
   assets/
       love_song.mp3
   ```

2. Place your MP3 file named `love_song.mp3` in the `assets` folder

3. The music will automatically play when the app starts

## 📦 Building .exe for Windows

### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

### Step 2: Build the Executable

#### Option A: Simple Build (no music)
```bash
pyinstaller --onefile --windowed --name="NeonHeart" neon_heart_app.py
```

#### Option B: Build with Music Included
```bash
pyinstaller --onefile --windowed --name="NeonHeart" --add-data "assets;assets" neon_heart_app.py
```

**Note for Windows**: Use `--add-data "assets;assets"` (with semicolon)
**Note for Linux/Mac**: Use `--add-data "assets:assets"` (with colon)

### Step 3: Find Your .exe

The compiled executable will be in the `dist` folder:
```
dist/
    NeonHeart.exe
```

### Step 4: Distribute

You can now share `NeonHeart.exe` with anyone! If you included music, make sure the `assets` folder is alongside the executable.

## 🔧 Build Script (Windows)

Create a file named `build.bat`:

```batch
@echo off
echo Building Neon Heart Application...
pip install pygame pyinstaller
pyinstaller --onefile --windowed --name="NeonHeart" --add-data "assets;assets" neon_heart_app.py
echo Build complete! Check the 'dist' folder for NeonHeart.exe
pause
```

Run it with:
```cmd
build.bat
```

## 🎨 Customization

You can modify the appearance by editing constants in the `Config` class:

```python
class Config:
    SCREEN_WIDTH = 800          # Window width
    SCREEN_HEIGHT = 600         # Window height
    FPS = 60                    # Frames per second
    
    HEART_BASE_SIZE = 100       # Heart size
    HEART_GLOW_RADIUS = 30      # Glow intensity
    HEART_PULSE_SPEED = 3       # Pulse speed
    HEART_PULSE_AMPLITUDE = 5   # Pulse strength
    
    RAINBOW_SPEED = 2           # Color cycle speed
    
    PARTICLE_COUNT = 50         # Max particles
    PARTICLE_LIFETIME = 120     # Particle lifetime (frames)
    
    TEXT_APPEAR_DELAY = 60      # Delay before text appears (frames)
```

## 📁 Project Structure

```
neon_heart_project/
├── neon_heart_app.py    # Main application (all-in-one)
├── assets/
│   └── love_song.mp3    # Optional background music
├── build.bat            # Windows build script
├── dist/
│   └── NeonHeart.exe    # Compiled executable
└── README.md            # This file
```

## 🐛 Troubleshooting

### No sound?
- Make sure the `assets/love_song.mp3` file exists
- Check that your system volume is up
- The app will run fine without music

### Low FPS?
- Reduce `PARTICLE_COUNT` in the Config class
- Lower the `FPS` setting
- Close other applications

### Build fails?
- Make sure you have Python installed and in PATH
- Run: `pip install --upgrade pip`
- Try running the build command as Administrator

## 💝 Made with Love

This application was created to express love through code. Enjoy sharing it with your special someone!

---

**License**: Free to use and modify for personal purposes.
**Author**: Created with ❤️
