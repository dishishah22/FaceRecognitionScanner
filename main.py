import cv2
import face_recognition
import os
import numpy as np


# Create a folder named 'known_faces' next to this main.py file.
# Put images of people you want to recognize inside it (e.g., 'dishi.jpg').
KNOWN_FACES_DIR = "known_faces"

known_face_encodings = []
known_face_names = []

# Check if the directory exists
if not os.path.exists(KNOWN_FACES_DIR):
    os.makedirs(KNOWN_FACES_DIR)
    print(f"Created folder '{KNOWN_FACES_DIR}'. Please put some images in it!")

# Load images from the known_faces directory
print("Loading known faces...")
for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.endswith((".jpg", ".jpeg", ".png")):
        # The name of the person is the filename without the extension
        name = os.path.splitext(filename)[0]
        filepath = os.path.join(KNOWN_FACES_DIR, filename)

        # Load the image file and encode the face
        image = face_recognition.load_image_file(filepath)
        encodings = face_recognition.face_encodings(image)
        
        # Make sure at least one face was found in the image
        if len(encodings) > 0:
            known_face_encodings.append(encodings[0])
            known_face_names.append(name.title()) # Capitalize the name
            print(f"✅ Loaded: {name.title()}")
        else:
            print(f"⚠️ Warning: No faces found in {filename}")

print("Face loading complete. Starting webcam...")

# Initialize the webcam (0 is usually the default laptop camera)
video_capture = cv2.VideoCapture(0)

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Resize frame to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        # Use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        
        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

        face_names.append(name)

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Choose color: Green if known, Red if Unknown
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Face Recognition Scanner', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
