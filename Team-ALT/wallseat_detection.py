import cv2
import streamlit as st
import time
from pose_utils import pose, mp_drawing, mp_pose, calculate_angle

# Add this to each exercise detection page
from database.models import WorkoutTracker
from auth.authenticator import get_authenticator

def wall_sit_tracker():
    st.subheader("📹 Wall Sit Tracker - Live Webcam Feed")
    stframe = st.empty()

    if 'sitting' not in st.session_state:
        st.session_state.sitting = False
        st.session_state.start_time = 0
        st.session_state.total_time = 0
        st.session_state.set_durations = []

    cap = cv2.VideoCapture(0)

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

            feedback = "Keep going!"

            if 80 <= knee_angle <= 100:
                feedback = "Perfect form! Hold it."
                if not st.session_state.sitting:
                    st.session_state.sitting = True
                    st.session_state.start_time = time.time()
            else:
                feedback = "Get into the wall sit position!"
                if st.session_state.sitting:
                    st.session_state.sitting = False
                    duration = time.time() - st.session_state.start_time
                    if duration > 2:
                        st.session_state.set_durations.append(int(duration))
                        st.session_state.total_time += duration
                        st.session_state.rep_count = len(st.session_state.set_durations)

            elapsed_time = (time.time() - st.session_state.start_time) if st.session_state.sitting else 0
            display_time = st.session_state.total_time + elapsed_time

            cv2.putText(frame, f"Total Time: {int(display_time)} sec", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(frame, f"Sets: {st.session_state.rep_count}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(frame, feedback, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


        stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)

    cap.release()
    cv2.destroyAllWindows()

 