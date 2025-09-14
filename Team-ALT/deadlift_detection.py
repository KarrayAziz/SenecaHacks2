import cv2
import streamlit as st
from pose_utils import pose, mp_drawing, mp_pose, calculate_angle

# Add this to each exercise detection page
from database.models import WorkoutTracker
from auth.authenticator import get_authenticator

def deadlift_tracker():
    st.subheader("📹 Deadlift Tracker - Live Webcam Feed")
    stframe = st.empty()
    cap = cv2.VideoCapture(0)
    bar_down = True

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
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            knee_angle = calculate_angle(hip, knee, ankle)
            arm_angle = calculate_angle(shoulder, elbow, wrist)

            feedback = "Lower the bar and maintain form!"

            if arm_angle < 170:
                feedback = "Keep your arms straight!"
            elif knee_angle > 160 and bar_down:
                feedback = "Good lockout! Lower now."
                bar_down = False
            elif knee_angle < 110 and not bar_down:
                st.session_state.rep_count += 1
                feedback = "Good rep! Lift again."
                bar_down = True

            cv2.putText(frame, feedback, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Reps: {st.session_state.rep_count}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)

    cap.release()
    cv2.destroyAllWindows()

 