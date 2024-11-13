import face_recognition
import pickle
import os
from datetime import datetime
import pandas as pd
from mtcnn import MTCNN
import cv2

def detect_attendance(image_path):
    # Load stored encodings and metadata
    try:
        with open('student_encodings.pkl', 'rb') as file:
            student_data = pickle.load(file)
    except FileNotFoundError:
        print("Error: No student data found. Run the enrollment script first.")
        return
    except Exception as e:
        print(f"Error loading student data: {e}")
        return

    # Extract encodings, names, and USNs
    known_face_encodings = [student['encodings'] for student in student_data]
    known_face_names = [student['name'] for student in student_data]
    known_face_usns = [student['usn'] for student in student_data]

    # Flatten the list of encodings for comparison
    flattened_encodings = [encoding for encodings in known_face_encodings for encoding in encodings]

    # Initialize MTCNN detector
    detector = MTCNN()

    # Load the classroom image using OpenCV for better compatibility with MTCNN
    try:
        image = cv2.imread(image_path)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    except Exception as e:
        print(f"Error loading the image: {e}")
        return

    # Detect faces in the image using MTCNN
    detected_faces = detector.detect_faces(rgb_image)

    print(f"Detected {len(detected_faces)} face(s) in the image.")

    # Prepare an attendance list
    attendance_list = []
    present_students = set()

    # Compare each detected face with the known faces
    for face in detected_faces:
        x, y, width, height = face['box']
        face_encoding = face_recognition.face_encodings(rgb_image, [(y, x + width, y + height, x)])[0]

        # Compare the detected face with known faces
        matches = face_recognition.compare_faces(flattened_encodings, face_encoding)
        face_distances = face_recognition.face_distance(flattened_encodings, face_encoding)
        best_match_index = None

        if face_distances.size > 0:
            best_match_index = face_distances.argmin()

        if best_match_index is not None and best_match_index < len(flattened_encodings):
            # Find the student who has this encoding
            student_index = 0
            encoding_offset = best_match_index
            for encodings in known_face_encodings:
                if encoding_offset < len(encodings):
                    break
                encoding_offset -= len(encodings)
                student_index += 1

            if student_index < len(known_face_names):
                name = known_face_names[student_index]
                usn = known_face_usns[student_index]

                # Add the student to the attendance list if not already added
                if usn not in present_students:
                    present_students.add(usn)
                    attendance_list.append({
                        'Name': name,
                        'USN': usn,
                        'Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            else:
                print(f"Error: Student index {student_index} out of range.")
        else:
            print("No match found for detected face.")

    # Get the list of all students' USNs
    all_usns = set(known_face_usns)

    # Determine the absent students
    absent_usns = all_usns - present_students
    absent_list = [{'Name': known_face_names[known_face_usns.index(usn)],
                    'USN': usn,
                    'Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")} for usn in absent_usns]

    # Convert to DataFrames
    present_df = pd.DataFrame(attendance_list)
    absent_df = pd.DataFrame(absent_list)

    # Save the attendance to an Excel file
    with pd.ExcelWriter('attendance.xlsx') as writer:
        present_df.to_excel(writer, sheet_name='Present Students', index=False)
        absent_df.to_excel(writer, sheet_name='Absent Students', index=False)

    print("Attendance has been saved successfully to 'attendance.xlsx'.")

# Example usage
image_path = input("Enter the path to the classroom image (e.g., 'classroom.jpg'): ")
detect_attendance(image_path)