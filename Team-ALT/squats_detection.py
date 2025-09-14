import cv2
import streamlit as st
from pose_utils import pose, mp_drawing, mp_pose, calculate_angle

# Add this to each exercise detection page
from database.models import WorkoutTracker
from auth.authenticator import get_authenticator

def squat_tracker():
    st.subheader("📹 Squat Tracker - Live Webcam Feed")
    stframe = st.empty()
    cap = cv2.VideoCapture(0)
    standing = True

    while cap.isOpened() and st.session_state.view == 'session':
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to capture webcam.")
            break

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            landmarks = results.pose_landmarks.landmark
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            knee_angle = calculate_angle(hip, knee, ankle)

            feedback = ""
            if knee_angle < 80:
                feedback = "Good squat!"
                if standing:
                    st.session_state.rep_count += 1
                    standing = False
            elif knee_angle > 170:
                feedback = "Stand up straight!"
                standing = True
            else:
                feedback = "Go lower!"

            cv2.putText(frame, feedback, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Reps: {st.session_state.rep_count}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)

    cap.release()
    cv2.destroyAllWindows()
