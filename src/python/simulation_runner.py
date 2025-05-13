import heat_model_viewer
import time
import sys

def main():
    try:
        print("Initializing renderer...")
        # Create renderer with a fixed size
        renderer = heat_model_viewer.Renderer(640, 480, "Simple Fixed Cube Demo")
        print("Renderer initialized successfully!")
        
        # Set camera to a fixed position
        renderer.set_camera_position(0.0, 0.0, 5.0)
        print("Camera positioned at (0, 0, 5) looking at origin")
        
        # Fixed rendering loop - no movement or animation
        print("Starting rendering loop...")
        frame_count = 0
        max_frames = 1000  # Limit total frames for testing
        
        while not renderer.should_close() and frame_count < max_frames:
            # Clear with a consistent color
            renderer.clear(0.2, 0.2, 0.3)
            
            # Render from fixed viewpoint
            renderer.render()
            
            # Print status periodically
            if frame_count % 10 == 0:
                print(f"Rendered frame {frame_count}")
            
            frame_count += 1
            
            # Maintain consistent timing
            time.sleep(0.1)  # Slower frame rate (10 FPS) for more stability
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
    print("Viewer exited successfully")