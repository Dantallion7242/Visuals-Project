import numpy as np
import pyaudio
import pygame
import time
import random
from scipy.fftpack import fft

# Initialize PyGame
pygame.init()

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# Initialize PyAudio
p = pyaudio.PyAudio()

# Create a window for visualization
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Define colors for visualization
base_color = (255, 255, 255)

# Define animation settings
circle_bounce_speed = 5
circle_radius_base = 20
circle_bounce = np.zeros(20)  # Bounce amplitude for each circle
circle_angle = np.zeros(20)  # Angle for rotation around the center
circle_gravity = np.zeros(20)  # Gravity effect on the circles
gravity_speed = 0.2  # Speed of gravity
gravity_limit = 250  # Limit for bounce

# Timer for glitches
glitch_timer = 0
glitch_interval = 30  # 20 seconds

# Fibonacci sequence setup for triangle visualization
fibonacci_index = 1
fibonacci_values = [0, 1]

# Function to track time elapsed
start_time = time.time()

# Audio callback function
# Audio callback function
def callback(in_data, frame_count, time_info, status):
    global audio_data
    audio_data = np.frombuffer(in_data, dtype=np.int16)
    
    # Get current time for calculating elapsed time
    current_time = time.time()
    time_elapsed = current_time - start_time
    
    # Process audio data for visualization
    amplitude, spectrum = get_audio_spectrum(audio_data)
    
    # Update visualization
    screen.fill((0, 0, 0))  # Clear the screen
    draw_background_glitches()
    draw_fractal_objects(amplitude)

    # Switch between circles and Fibonacci triangles based on time
    if time_elapsed > 44:
        draw_fibonacci_triangle(amplitude, time_elapsed)
    else:
        draw_circles(amplitude, time_elapsed)

    pygame.display.flip()

    return (in_data, pyaudio.paContinue)


# Function to compute amplitude and frequency spectrum from audio input
def get_audio_spectrum(data):
    fft_data = np.abs(fft(data)[:CHUNK // 1])  # Only take the positive frequencies
    amplitude = np.max(np.abs(data))  # Amplitude
    return amplitude, fft_data

def color_cycle(base_color, offset):
    r = (base_color[0] + offset * 2) % 256
    g = (base_color[1] + offset * 3) % 256
    b = (base_color[2] + offset * 4) % 256
    
    r = (r + int(128 * np.sin(offset / 10))) % 256
    g = (g + int(128 * np.cos(offset / 10))) % 256
    b = (b + int(128 * np.sin(offset / 15))) % 256

    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))

    return (r, g, b)

def draw_circles(amplitude, time_elapsed):
    num_circles = 10
    global circle_bounce, circle_angle, circle_gravity

    fib_sequence = [0, 1]
    for i in range(2, num_circles):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])

    depth_scaling_factor = 0.5  # Adjusts the scale for the z-depth transformation
    depth_translation = 100  # Distance from the "viewer" to the screen in 3D space

    for i in range(num_circles):
        # Original circle size and position
        radius = fib_sequence[i] % 70 + (amplitude / 10)
        circle_angle[i] += 0.05 * (i + 1)

        # Introduce a "z-axis" component by creating depth
        z_depth = depth_translation + depth_scaling_factor * i  # z-depth transformation
        x = screen_width // 2 + (z_depth * np.cos(circle_angle[i]))
        y = screen_height // 2 + (z_depth * np.sin(circle_angle[i]))

        # Gravity effect (with bounce)
        circle_gravity[i] += gravity_speed
        if y + circle_gravity[i] > screen_height - gravity_limit:
            circle_gravity[i] = -abs(circle_gravity[i]) * 0.8

        y += circle_gravity[i]

        # The size of the circle will now depend on its z-depth (closer circles appear bigger)
        shapeshift_factor = 1 + (amplitude / 300)
        scaled_radius = int(radius * shapeshift_factor)

        # Gradually increase the radius as they move toward the center
        transformed_radius = int(scaled_radius * (depth_translation / z_depth))

        # Dynamic color cycling for 3D depth effect
        color = color_cycle(base_color, i * 10)

        # Draw circles with pseudo-3D effect
        pygame.draw.circle(screen, color, (int(x), int(y)), transformed_radius, width=1)

def draw_fibonacci_triangle(amplitude, time_elapsed):
    global fibonacci_index, fibonacci_values

    # Check if 44 seconds have passed
    if time_elapsed > 44:
        if len(fibonacci_values) <= fibonacci_index:
            fibonacci_values.append(fibonacci_values[-1] + fibonacci_values[-2])

        fib_value = fibonacci_values[fibonacci_index % len(fibonacci_values)]
        size = fib_value * 5
        triangle_points = [
            (screen_width // 2, screen_height // 2 - size),
            (screen_width // 2 - size, screen_height // 2 + size),
            (screen_width // 2 + size, screen_height // 2 + size)
        ]

        color = color_cycle(base_color, fibonacci_index * 10)
        pygame.draw.polygon(screen, color, triangle_points, width=1)

        fibonacci_index += 1
    else:
        # Call draw_circles if time_elapsed < 44 seconds
        draw_circles(amplitude, time_elapsed)

def draw_background_glitches():
    global glitch_timer
    current_time = time.time()

    if current_time - glitch_timer > glitch_interval:
        glitch_timer = current_time

        for _ in range(100):
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            w = random.randint(20, 50)
            h = random.randint(20, 50)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            pygame.draw.rect(screen, color, (x, y, w, h))



def draw_fractal_objects(amplitude):
    def draw_recursive_fractal(x, y, size, depth):
        if depth == 0:
            return
        pygame.draw.circle(screen, (random.randint(100, 255), random.randint(100, 255), 255), (int(x), int(y)), size, 1)
        new_size = size // 2
        draw_recursive_fractal(x + new_size, y, new_size, depth - 1)
        draw_recursive_fractal(x - new_size, y, new_size, depth - 1)
        draw_recursive_fractal(x, y + new_size, new_size, depth - 1)
        draw_recursive_fractal(x, y - new_size, new_size, depth - 1)

    if time.time() - glitch_timer < 3:
        for _ in range(5):
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            size = random.randint(20, 50)
            depth = random.randint(2, 4)
            draw_recursive_fractal(x, y, size, depth)

def draw_fibonacci_triangle(amplitude, spectrum):
    global fibonacci_index, fibonacci_values

    if len(fibonacci_values) <= fibonacci_index:
        fibonacci_values.append(fibonacci_values[-1] + fibonacci_values[-2])

    if amplitude > 20000:
        fib_value = fibonacci_values[fibonacci_index % len(fibonacci_values)]
        size = fib_value * 5
        triangle_points = [
            (screen_width // 2, screen_height // 2 - size),
            (screen_width // 2 - size, screen_height // 2 + size),
            (screen_width // 2 + size, screen_height // 2 + size)
        ]
        
        color = color_cycle(base_color, fibonacci_index * 10)
        pygame.draw.polygon(screen, color, triangle_points, width=1)

        fibonacci_index += 1

# Open input and output streams
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=callback)

# Start the stream
stream.start_stream()

# Main loop for visualization
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    time.sleep(0.01)

# Clean up resources
stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()
