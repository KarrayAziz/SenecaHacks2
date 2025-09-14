# wallsit_detection.py
import cv2
import streamlit as st
import time
from pose_utils import pose, mp_drawing, mp_pose, calculate_angle

def wall_sit_tracker():
    st.subheader("📹 Wall Sit Tracker - Live Webcam Feed")
    stframe = st.empty()

    if 'sitting' not in st.session_state:
        st.session_state.sitting = False
        st.session_state.start_time = 0
        st.session_state.total_time = 0
        st.session_state.set_durations = []
        st.session_state.rep_count = 0 # Initialiser rep_count pour les sets

    cap = cv2.VideoCapture(0)

    # Définition des couleurs pour le feedback (identique à bicepcurls)
    COLOR_BLUE = (255, 0, 0)
    COLOR_ORANGE = (0, 165, 255)
    COLOR_GREEN = (0, 255, 0)

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

            feedback = "Get into position!"
            color = COLOR_ORANGE

            if 80 <= knee_angle <= 100:
                feedback = "Perfect form! Hold it."
                color = COLOR_GREEN
                if not st.session_state.sitting:
                    st.session_state.sitting = True
                    st.session_state.start_time = time.time()
            else:
                feedback = "Get into position!"
                color = COLOR_ORANGE
                if st.session_state.sitting:
                    st.session_state.sitting = False
                    duration = time.time() - st.session_state.start_time
                    if duration > 2: # Valider la série si elle a duré plus de 2s
                        st.session_state.set_durations.append(int(duration))
                        st.session_state.total_time += duration
                        st.session_state.rep_count = len(st.session_state.set_durations)

            elapsed_time = (time.time() - st.session_state.start_time) if st.session_state.sitting else 0
            display_time = st.session_state.total_time + elapsed_time
            
            # --- Affichage sur l'écran (style bicepcurls, adapté pour le temps) ---
            cv2.putText(frame, feedback, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.putText(frame, f"Total Time: {int(display_time)}s", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
            cv2.putText(frame, f"Sets: {st.session_state.rep_count}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)


        # Affichage de l'image dans Streamlit (avec les bons canaux)
        stframe.image(frame, channels="BGR", use_container_width=True)

    cap.release()
    cv2.destroyAllWindows()