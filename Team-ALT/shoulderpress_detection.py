import cv2
import streamlit as st
from pose_utils import pose, mp_drawing, mp_pose, calculate_angle

def shoulder_press_tracker():
    st.subheader("📹 Shoulder Press Tracker - Live Webcam Feed")
    stframe = st.empty()
    cap = cv2.VideoCapture(0)
    arms_down = False

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

            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            angle = calculate_angle(shoulder, elbow, wrist)

            feedback = "Now Down!"

            if angle > 160:
                feedback = "Arms Up!"
                arms_down = False
            elif angle < 70:
                feedback = "Go Up!"
                if not arms_down:
                    st.session_state.rep_count += 1
                    arms_down = True

            cv2.putText(frame, feedback, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Reps: {st.session_state.rep_count}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)

    cap.release()
    cv2.destroyAllWindows()