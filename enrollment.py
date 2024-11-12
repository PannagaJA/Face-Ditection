import face_recognition
import pickle
import os
from datetime import datetime

def enroll_student_from_image(image_path, name, usn):
    # Check if the image path is valid
    if not os.path.isfile(image_path):
        print("Error: The file path provided does not exist or is invalid.")
        return
    
    # Load the uploaded image
    try:
        student_image = face_recognition.load_image_file(image_path)
    except Exception as e:
        print(f"Error loading the image: {e}")
        return
    
    # Find face locations and encodings in the image
    face_locations = face_recognition.face_locations(student_image)
    face_encodings = face_recognition.face_encodings(student_image, face_locations)

    if not face_encodings:
        print("No faces detected in the uploaded image. Please upload an image with a clear face.")
        return

    if len(face_encodings) > 1:
        print(f"Multiple faces detected. Using the first face detected.")
        face_encoding = face_encodings[0]
    else:
        face_encoding = face_encodings[0]

    # Load existing student data or create a new list
    try:
        with open('student_encodings.pkl', 'rb') as file:
            student_data = pickle.load(file)
    except FileNotFoundError:
        student_data = []

    # Check if the student is already enrolled (by USN)
    student_found = False
    for student in student_data:
        if student['usn'] == usn:
            # Check if the face encoding is already registered for this student
            matches = face_recognition.compare_faces(student['encodings'], face_encoding)
            if True in matches:
                print(f"Student {name} ({usn}) is already enrolled and registered.")
                return  # Exit without adding the encoding if it's a duplicate
            else:
                # Add the new face encoding to the student's record
                student['encodings'].append(face_encoding)
                student_found = True
                break

    if not student_found:
        # Add new student with face encoding
        student_data.append({
            'name': name,
            'usn': usn,
            'encodings': [face_encoding]  # Store all encodings in a list
        })

    # Save the updated student data to the pickle file
    try:
        with open('student_encodings.pkl', 'wb') as file:
            pickle.dump(student_data, file)
        print(f"Student {name} ({usn}) has been successfully enrolled with face encoding.")
    except Exception as e:
        print(f"Error saving student data: {e}")

# Example of how to use the function
def enroll_students():
    num_students = int(input("How many students to enroll? "))
    for _ in range(num_students):
        image_path = input("Enter the path to the student's photo (e.g., 'student_photo.jpg'): ")
        name = input("Enter the student's name: ")
        usn = input("Enter the student's USN: ")
        enroll_student_from_image(image_path, name, usn)

enroll_students()
