import face_recognition
import pickle
from datetime import datetime

def detect_attendance(image_path, threshold=0.6):  # Default threshold to 0.6
    # Load stored student data (encodings, names, and USNs)
    try:
        with open('student_encodings.pkl', 'rb') as file:
            student_data = pickle.load(file)
    except FileNotFoundError:
        print("Error: No student data found. Please run the enrollment script first.")
        return

    # Extract encodings, names, and USNs
    known_face_encodings = [student['encodings'] for student in student_data]
    known_face_names = [student['name'] for student in student_data]
    known_face_usns = [student['usn'] for student in student_data]

    # Flatten the list of encodings for comparison
    flattened_encodings = [encoding for encodings in known_face_encodings for encoding in encodings]

    # Load the classroom image
    try:
        classroom_image = face_recognition.load_image_file(image_path)
    except Exception as e:
        print(f"Error loading the image: {e}")
        return

    # Detect face locations and encodings in the classroom image
    face_locations = face_recognition.face_locations(classroom_image)
    face_encodings = face_recognition.face_encodings(classroom_image, face_locations)

    # Prepare attendance lists
    present_list = []
    absent_list = []

    # Compare each detected face with the known faces
    for face_encoding in face_encodings:
        # Compare face encoding to all known encodings and calculate distances
        distances = face_recognition.face_distance(flattened_encodings, face_encoding)
        
        # Find the index of the minimum distance (closest match)
        best_match_index = distances.argmin()
        
        # If the distance is below the threshold, consider it a match
        if distances[best_match_index] <= threshold:
            name = known_face_names[best_match_index]
            usn = known_face_usns[best_match_index]
            present_list.append({'Name': name, 'USN': usn, 'Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        else:
            present_list.append({'Name': 'Unknown', 'USN': 'N/A', 'Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    # Determine who is absent (those who were not detected)
    detected_names = [entry['Name'] for entry in present_list]
    absent_list = [student for student in student_data if student['name'] not in detected_names]

    # Saving the attendance data to a text file
    try:
        with open('attendance.txt', 'w') as file:
            file.write("Attendance Record\n")
            file.write("="*40 + "\n")
            file.write("Present Students:\n")
            for entry in present_list:
                file.write(f"{entry['Name']} ({entry['USN']}) - {entry['Time']}\n")
            file.write("\nAbsent Students:\n")
            for student in absent_list:
                file.write(f"{student['name']} ({student['usn']})\n")
        print("Attendance has been saved successfully to 'attendance.txt'.")
    except Exception as e:
        print(f"Error saving attendance data: {e}")

# Example of how to use the function
image_path = input("Enter the path to the classroom image (e.g., 'classroom.jpg'): ")
detect_attendance(image_path)
