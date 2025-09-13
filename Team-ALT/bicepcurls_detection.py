import cv2
import streamlit as st
from pose_utils import pose, mp_drawing, mp_pose, calculate_angle

def bicep_curl_tracker():
    st.subheader("📹 Bicep Curl Tracker - Live Webcam Feed")
    stframe = st.empty()
    cap = cv2.VideoCapture(0)

    right_arm_extended = True
    left_arm_extended = True

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

            # Right Arm
            right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
            right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

            if right_elbow_angle < 50:
                if right_arm_extended:
                    st.session_state.right_rep_count += 1
                    right_arm_extended = False
            elif right_elbow_angle > 150:
                right_arm_extended = True

            # Left Arm
            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)

            if left_elbow_angle < 50:
                if left_arm_extended:
                    st.session_state.left_rep_count += 1
                    left_arm_extended = False
            elif left_elbow_angle > 150:
                left_arm_extended = True

            # Display rep counts
            cv2.putText(frame, f"Right Curls: {st.session_state.right_rep_count}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
            cv2.putText(frame, f"Left Curls: {st.session_state.left_rep_count}", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)

    cap.release()
    cv2.destroyAllWindows()