# bicepcurls_detection.py
import cv2
import streamlit as st
from pose_utils import pose, mp_drawing, mp_pose, calculate_angle


def bicep_curl_tracker():
    st.subheader("📹 Bicep Curl Tracker - Live Webcam Feed")
    
    # Create columns for layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        stframe = st.empty()
    
    with col2:
        # Stop button
        if st.button("🛑 Stop Session", type="primary", use_container_width=True):
            st.session_state.view = 'home'  # or whatever your home view is called
            st.rerun()
        
        # Display current counts
        st.metric("Right Curls", st.session_state.right_rep_count)
        st.metric("Left Curls", st.session_state.left_rep_count)
        
        # Reset button (optional)
        if st.button("🔄 Reset Counters", use_container_width=True):
            st.session_state.right_rep_count = 0
            st.session_state.left_rep_count = 0
    
    cap = cv2.VideoCapture(0)

    # État des bras (ne doit pas être dans session_state, car il est géré à chaque frame)
    right_arm_extended = True
    left_arm_extended = True

    # Définition des couleurs pour le feedback (format BGR pour OpenCV)
    COLOR_BLUE = (255, 0, 0)
    COLOR_ORANGE = (0, 165, 255)
    COLOR_GREEN = (0, 255, 0)

    # Boucle principale qui s'arrête correctement lorsque l'utilisateur quitte la session
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to capture webcam. Please check your camera settings.")
            break

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
            )
            landmarks = results.pose_landmarks.landmark

            # --- Logique pour le Bras Droit ---
            right_shoulder = [
                landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y,
            ]
            right_elbow = [
                landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y,
            ]
            right_wrist = [
                landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y,
            ]
            right_elbow_angle = calculate_angle(
                right_shoulder, right_elbow, right_wrist
            )

            # Feedback visuel pour le bras droit
            if right_elbow_angle > 150:
                feedback_right = "Right Arm Extended"
                color_right = COLOR_BLUE
                right_arm_extended = True
            elif right_elbow_angle < 10:
                feedback_right = "Good Right Curl!"
                color_right = COLOR_GREEN
                # Comptage de la répétition en utilisant st.session_state
                if right_arm_extended:
                    st.session_state.right_rep_count += 1
                    right_arm_extended = False
            else:
                feedback_right = "Curl More!"
                color_right = COLOR_ORANGE

            # --- Logique pour le Bras Gauche ---
            left_shoulder = [
                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y,
            ]
            left_elbow = [
                landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y,
            ]
            left_wrist = [
                landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y,
            ]
            left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)

            # Feedback visuel pour le bras gauche
            if left_elbow_angle > 150:
                feedback_left = "Left Arm Extended"
                color_left = COLOR_BLUE
                left_arm_extended = True
            elif left_elbow_angle < 10:
                feedback_left = "Good Left Curl!"
                color_left = COLOR_GREEN
                # Comptage de la répétition en utilisant st.session_state
                if left_arm_extended:
                    st.session_state.left_rep_count += 1
                    left_arm_extended = False
            else:
                feedback_left = "Curl More!"
                color_left = COLOR_ORANGE

            # --- Affichage sur l'écran ---
            # Affichage des feedbacks
            cv2.putText(
                frame, feedback_right, (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color_right, 2
            )
            cv2.putText(
                frame, feedback_left, (50, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color_left, 2
            )

            # Affichage des compteurs de répétitions (qui sont maintenant persistants)
            cv2.putText(
                frame, f"Right Curls: {st.session_state.right_rep_count}",
                (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2
            )
            cv2.putText(
                frame, f"Left Curls: {st.session_state.left_rep_count}",
                (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2
            )

        # Affichage de l'image dans Streamlit
        stframe.image(frame, channels="BGR", use_container_width=True)

    cap.release()
    cv2.destroyAllWindows()


def save_workout_session(user_id: int):
    """Save the current bicep curl session data to the database"""
    try:
        # Calculate session metrics
        total_reps = st.session_state.right_rep_count + st.session_state.left_rep_count
        session_duration = datetime.now() - st.session_state.session_start_time
        duration_minutes = int(session_duration.total_seconds() / 60)
        
        # Estimate calories burned (rough estimate: 5 calories per minute for bicep curls)
        calories_burned = duration_minutes * 5.0
        
        # Calculate a basic form score (this could be enhanced with actual form analysis)
        # For now, we'll use a simple metric based on rep consistency
        form_score = min(8.5, 6.0 + (total_reps * 0.1))  # Simple scoring system
        
        # Initialize database connection and workout tracker
        db_manager = DatabaseManager()
        workout_tracker = WorkoutTracker(db_manager)
        
        # Save workout to database
        success = workout_tracker.log_workout(
            user_id=user_id,
            exercise_type="Bicep Curls",
            duration=duration_minutes,
            reps=total_reps,
            sets=1,  # Assuming one continuous set
            calories_burned=calories_burned,
            form_score=form_score,
            notes=f"Right arm: {st.session_state.right_rep_count} reps, Left arm: {st.session_state.left_rep_count} reps"
        )
        
        if success:
            st.success(f"✅ Workout saved! {total_reps} total reps in {duration_minutes} minutes")
        else:
            st.error("❌ Failed to save workout data")
            
    except Exception as e:
        st.error(f"❌ Error saving workout: {str(e)}")


def reset_session_counters():
    """Reset all session counters and start time"""
    st.session_state.right_rep_count = 0
    st.session_state.left_rep_count = 0
    st.session_state.session_start_time = datetime.now()