"""
Neon Heart Animation - Desktop Application
A beautiful animated neon heart with particles and glowing effects.

Structure:
- main.py: Entry point and application loop
- heart.py: Heart animation logic
- particles.py: Particle system for sparkles
- text_renderer.py: Neon text rendering
- audio.py: Sound management
- config.py: Configuration constants
"""

import pygame
import math
import random
import sys
from pathlib import Path

# Initialize pygame
pygame.init()
pygame.mixer.init()

# ============== CONFIGURATION ==============
class Config:
    """Application configuration constants"""
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS = 60
    TITLE = "Для Енечки 💖"
    
    # Colors (RGB)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    
    # Heart settings
    HEART_BASE_SIZE = 100
    HEART_GLOW_RADIUS = 30
    HEART_PULSE_SPEED = 3
    HEART_PULSE_AMPLITUDE = 5
    
    # Rainbow cycle speed (degrees per frame)
    RAINBOW_SPEED = 2
    
    # Particle settings
    PARTICLE_COUNT = 50
    PARTICLE_LIFETIME = 120  # frames
    PARTICLE_SPEED_MIN = 1
    PARTICLE_SPEED_MAX = 4
    
    # Text settings
    TEXT_Y_OFFSET = 150
    TEXT_FADE_SPEED = 3
    TEXT_APPEAR_DELAY = 60  # frames after heart appears
    
    # Audio settings
    AUDIO_ENABLED = True
    
    # Paths
    ASSETS_DIR = Path(__file__).parent / "assets"
    AUDIO_FILE = ASSETS_DIR / "love_song.mp3"


# ============== HEART RENDERER ==============
class HeartRenderer:
    """Renders the animated neon heart with rainbow gradient"""
    
    def __init__(self, center_x, center_y):
        self.center_x = center_x
        self.center_y = center_y
        self.base_size = Config.HEART_BASE_SIZE
        self.current_size = 0
        self.target_size = self.base_size
        self.fade_in = True
        self.pulse_phase = 0
        self.hue_angle = 0  # For rainbow effect
        
    def get_heart_points(self, size, angle_offset=0):
        """Generate heart shape points using parametric equation"""
        points = []
        num_points = 100
        
        for i in range(num_points):
            t = (i / num_points) * 2 * math.pi
            
            # Heart parametric equations
            x = 16 * (math.sin(t) ** 3)
            y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 
                  2 * math.cos(3*t) - math.cos(4*t))
            
            # Rotate slightly for better orientation
            x_rot = x * math.cos(angle_offset) - y * math.sin(angle_offset)
            y_rot = x * math.sin(angle_offset) + y * math.cos(angle_offset)
            
            # Scale and position
            px = self.center_x + x_rot * (size / 16)
            py = self.center_y + y_rot * (size / 16)
            
            points.append((px, py))
        
        return points
    
    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB color"""
        h = h % 360
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        
        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))
    
    def get_rainbow_color(self):
        """Get current rainbow color based on hue angle"""
        return self.hsv_to_rgb(self.hue_angle, 1.0, 1.0)
    
    def update(self):
        """Update heart animation state"""
        # Fade in effect
        if self.fade_in:
            if self.current_size < self.target_size:
                self.current_size += 2
            else:
                self.fade_in = False
        
        # Pulse effect after fade in
        if not self.fade_in:
            self.pulse_phase += Config.HEART_PULSE_SPEED * 0.05
            pulse = math.sin(self.pulse_phase) * Config.HEART_PULSE_AMPLITUDE
            self.current_size = self.target_size + pulse
        
        # Rainbow color cycling
        self.hue_angle = (self.hue_angle + Config.RAINBOW_SPEED) % 360
    
    def draw(self, screen):
        """Draw the heart with glow and rainbow effect"""
        if self.current_size <= 0:
            return
        
        # Get current rainbow color
        base_color = self.get_rainbow_color()
        
        # Create multiple surfaces for glow effect (blur simulation)
        glow_layers = [
            (Config.HEART_GLOW_RADIUS, 0.3),
            (Config.HEART_GLOW_RADIUS * 0.7, 0.5),
            (Config.HEART_GLOW_RADIUS * 0.4, 0.7),
        ]
        
        # Draw glow layers (back to front, dimmer to brighter)
        for radius, alpha in glow_layers:
            glow_surface = pygame.Surface((screen.get_width(), screen.get_height()), 
                                         pygame.SRCALPHA)
            points = self.get_heart_points(self.current_size + radius * 0.5)
            
            # Create gradient color for this layer
            glow_color = (*base_color, int(255 * alpha))
            
            if len(points) > 2:
                pygame.draw.polygon(glow_surface, glow_color, points)
            
            screen.blit(glow_surface, (0, 0))
        
        # Draw main heart (brightest)
        points = self.get_heart_points(self.current_size)
        if len(points) > 2:
            # Draw filled heart
            pygame.draw.polygon(screen, base_color, points)
            
            # Draw outline (brighter)
            outline_color = tuple(min(c + 50, 255) for c in base_color)
            pygame.draw.polygon(screen, outline_color, points, 3)


# ============== PARTICLE SYSTEM ==============
class Particle:
    """Individual particle for sparkle effects"""
    
    def __init__(self, x, y, heart_color):
        self.x = x
        self.y = y
        
        # Random velocity direction
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(Config.PARTICLE_SPEED_MIN, Config.PARTICLE_SPEED_MAX)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.lifetime = Config.PARTICLE_LIFETIME
        self.max_lifetime = Config.PARTICLE_LIFETIME
        self.size = random.uniform(2, 5)
        self.color = heart_color
        self.gravity = 0.05
        
    def update(self):
        """Update particle position and lifetime"""
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity  # Add slight gravity
        self.lifetime -= 1
        
        # Shrink over time
        self.size = max(0, self.size * 0.99)
        
    def is_alive(self):
        """Check if particle is still visible"""
        return self.lifetime > 0 and self.size > 0.5
    
    def draw(self, screen):
        """Draw the particle with fade effect"""
        if not self.is_alive():
            return
        
        # Calculate alpha based on lifetime
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        # Create particle surface with transparency
        particle_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), 
                                         pygame.SRCALPHA)
        
        # Draw glowing particle
        color_with_alpha = (*self.color, alpha)
        pygame.draw.circle(particle_surface, color_with_alpha, 
                          (int(self.size), int(self.size)), int(self.size))
        
        screen.blit(particle_surface, (int(self.x - self.size), 
                                       int(self.y - self.size)))


class ParticleSystem:
    """Manages all particles in the scene"""
    
    def __init__(self):
        self.particles = []
        self.spawn_timer = 0
        self.spawn_interval = 5  # Spawn particle every N frames
        
    def spawn_particle(self, center_x, center_y, heart_size, heart_color):
        """Spawn a new particle from heart area"""
        # Random position around heart
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, heart_size * 0.8)
        
        x = center_x + math.cos(angle) * distance
        y = center_y + math.sin(angle) * distance
        
        particle = Particle(x, y, heart_color)
        self.particles.append(particle)
    
    def update(self, heart_renderer):
        """Update all particles and spawn new ones"""
        # Spawn new particles periodically
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval and not heart_renderer.fade_in:
            self.spawn_particle(
                heart_renderer.center_x,
                heart_renderer.center_y,
                heart_renderer.current_size,
                heart_renderer.get_rainbow_color()
            )
            self.spawn_timer = 0
        
        # Update existing particles
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)
    
    def draw(self, screen):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen)


# ============== TEXT RENDERER ==============
class TextRenderer:
    """Renders neon-style text with glow effect"""
    
    def __init__(self, text, font_size=48):
        self.text = text
        self.font_size = font_size
        self.font = None
        self.alpha = 0
        self.target_alpha = 255
        self.visible = False
        self.hue_angle = 0
        
    def initialize_font(self):
        """Initialize font (call after pygame init)"""
        # Try to use a nice font, fallback to default
        try:
            self.font = pygame.font.SysFont('arial', self.font_size, bold=True)
        except:
            self.font = pygame.font.Font(None, self.font_size)
    
    def start_appearing(self):
        """Start the fade-in animation"""
        self.visible = True
        
    def update(self):
        """Update text animation"""
        if self.visible and self.alpha < self.target_alpha:
            self.alpha += Config.TEXT_FADE_SPEED
            if self.alpha > self.target_alpha:
                self.alpha = self.target_alpha
        
        # Cycle colors like rainbow
        self.hue_angle = (self.hue_angle + Config.RAINBOW_SPEED) % 360
    
    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB color"""
        h = h % 360
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        
        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))
    
    def draw(self, screen, center_x, center_y):
        """Draw the text with neon glow effect"""
        if not self.visible or self.alpha <= 0:
            return
        
        # Get rainbow color
        base_color = self.hsv_to_rgb(self.hue_angle, 1.0, 1.0)
        
        # Apply alpha
        color_with_alpha = tuple([*base_color, int(self.alpha)])
        
        # Render text
        text_surface = self.font.render(self.text, True, base_color)
        text_rect = text_surface.get_rect(center=(center_x, center_y))
        
        # Create glow effect with multiple layers
        glow_offsets = [(2, 2), (-2, -2), (2, -2), (-2, 2),
                       (1, 0), (-1, 0), (0, 1), (0, -1)]
        
        for offset in glow_offsets:
            glow_surface = self.font.render(self.text, True, base_color)
            glow_rect = glow_surface.get_rect(center=(center_x + offset[0], 
                                                       center_y + offset[1]))
            screen.blit(glow_surface, glow_rect)
        
        # Draw main text
        screen.blit(text_surface, text_rect)


# ============== AUDIO MANAGER ==============
class AudioManager:
    """Handles background music and sound effects"""
    
    def __init__(self):
        self.music_loaded = False
        self.music_playing = False
        
    def load_music(self, filepath):
        """Load background music from file"""
        try:
            if Path(filepath).exists():
                pygame.mixer.music.load(filepath)
                self.music_loaded = True
                print(f"Music loaded: {filepath}")
            else:
                print(f"Music file not found: {filepath}")
                self.music_loaded = False
        except Exception as e:
            print(f"Error loading music: {e}")
            self.music_loaded = False
    
    def play_music(self, loops=-1, volume=0.3):
        """Start playing background music"""
        if self.music_loaded and not self.music_playing:
            try:
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(loops)
                self.music_playing = True
                print("Music started")
            except Exception as e:
                print(f"Error playing music: {e}")
    
    def stop_music(self):
        """Stop background music"""
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False
    
    def play_sound_effect(self, filepath, volume=0.5):
        """Play a one-time sound effect"""
        try:
            if Path(filepath).exists():
                sound = pygame.mixer.Sound(filepath)
                sound.set_volume(volume)
                sound.play()
        except Exception as e:
            print(f"Error playing sound effect: {e}")


# ============== MAIN APPLICATION ==============
class NeonHeartApp:
    """Main application class managing the entire animation"""
    
    def __init__(self):
        # Setup display
        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption(Config.TITLE)
        self.clock = pygame.time.Clock()
        
        # Create components
        center_x = Config.SCREEN_WIDTH // 2
        center_y = Config.SCREEN_HEIGHT // 2 - 50
        
        self.heart = HeartRenderer(center_x, center_y)
        self.particles = ParticleSystem()
        self.text = TextRenderer("люблю тебя, енечка 💖", 48)
        self.audio = AudioManager()
        
        # State
        self.running = True
        self.frame_count = 0
        self.text_triggered = False
        
        # Initialize text font
        self.text.initialize_font()
        
        # Try to load music
        if Config.AUDIO_ENABLED:
            self.audio.load_music(Config.AUDIO_FILE)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    # Any key restarts the animation
                    self.restart()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Click restarts the animation
                self.restart()
    
    def restart(self):
        """Restart the entire animation"""
        self.heart = HeartRenderer(
            Config.SCREEN_WIDTH // 2,
            Config.SCREEN_HEIGHT // 2 - 50
        )
        self.particles = ParticleSystem()
        self.text = TextRenderer("люблю тебя, енечка 💖", 48)
        self.text.initialize_font()
        self.frame_count = 0
        self.text_triggered = False
        
        # Restart music
        if Config.AUDIO_ENABLED:
            self.audio.stop_music()
            self.audio.play_music()
    
    def update(self):
        """Update all animation components"""
        self.frame_count += 1
        
        # Update heart
        self.heart.update()
        
        # Update particles
        self.particles.update(self.heart)
        
        # Trigger text appearance after delay
        if not self.text_triggered and self.frame_count >= Config.TEXT_APPEAR_DELAY:
            self.text.start_appearing()
            self.text_triggered = True
            
            # Play sound effect when text appears (optional)
            # self.audio.play_sound_effect(Config.ASSETS_DIR / "chime.wav")
        
        # Update text
        self.text.update()
    
    def draw(self):
        """Render everything to screen"""
        # Clear screen with black background
        self.screen.fill(Config.BLACK)
        
        # Draw components in order
        self.particles.draw(self.screen)
        self.heart.draw(self.screen)
        self.text.draw(self.screen, Config.SCREEN_WIDTH // 2, 
                      Config.SCREEN_HEIGHT // 2 + Config.TEXT_Y_OFFSET)
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main application loop"""
        # Start music if available
        if Config.AUDIO_ENABLED:
            self.audio.play_music()
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(Config.FPS)
        
        # Cleanup
        if Config.AUDIO_ENABLED:
            self.audio.stop_music()
        pygame.quit()
        sys.exit()


# ============== ENTRY POINT ==============
def main():
    """Application entry point"""
    print("Starting Neon Heart Animation...")
    print("Press ESC to quit, any other key or click to restart")
    
    app = NeonHeartApp()
    app.run()


if __name__ == "__main__":
    main()
