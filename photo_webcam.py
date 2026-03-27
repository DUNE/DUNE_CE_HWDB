import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os

class photo_webcam:
    def __init__(self, window):
        self.window = window
        self.window.title("Python Webcam Photo Booth")
        
        # Initialize video capture
        self.video_capture = cv2.VideoCapture(0)
        #width, height = 1280,720
        width, height = 1920,1080
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                
        # UI Elements
        self.canvas = tk.Canvas(window, width=1920, height=1080)
        self.canvas.pack()
        
        self.btn_snapshot = tk.Button(window, text="Take Photo", command=self.take_snapshot)
        self.btn_snapshot.pack(pady=10)
        
        # Start the video loop
        self.update_frame()
        self.window.mainloop()

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            # Convert BGR (OpenCV) to RGB (Tkinter)
            self.current_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            self.photo = ImageTk.PhotoImage(image=self.current_image)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        
        # Repeat after 15ms (approx 60fps)
        self.window.after(15, self.update_frame)

    def take_snapshot(self):
        # Save the current frame to a file
        filename = "photo.jpg"
        self.current_image.save(filename)
        print(f"Photo saved as {filename}")

# Run the app
if __name__ == "__main__":
    photo_webcam(tk.Tk())
