# bicep_curls_detection.py
import cv2
import streamlit as st
from pose_utils import pose, mp_drawing, mp_pose, calculate_angle
from database.models import DatabaseManager, WorkoutTracker
from auth.authenticator import get_authenticator
from datetime import datetime
import time

# Initialize authenticator
auth = get_authenticator()

def initialize_session_state():
    """Initialize all session state variables for bicep curl tracking"""
    if 'right_rep_count' not in st.session_state:
        st.session_state.right_rep_count = 0
    if 'left_rep_count' not in st.session_state:
        st.session_state.left_rep_count = 0
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = datetime.now()
    if 'workout_saved' not in st.session_state:
        st.session_state.workout_saved = False
    if 'session_active' not in st.session_state:
        st.session_state.session_active = True

def save_workout_session(user_id: int):
    """Save the current bicep curl session data to the database"""
    try:
        # Calculate session metrics
        total_reps = st.session_state.right_rep_count + st.session_state.left_rep_count
        
        # Only save if there are reps recorded
        if total_reps == 0:
            st.warning("⚠️ No repetitions recorded. Workout not saved.")
            return False
        
        session_end_time = datetime.now()
        session_duration = session_end_time - st.session_state.session_start_time
        duration_minutes = max(1, int(session_duration.total_seconds() / 60))  # Minimum 1 minute
        
        # Estimate calories burned (rough estimate: 5 calories per minute for bicep curls)
        calories_burned = round(duration_minutes * 5.0, 1)
        
        # Calculate a basic form score (this could be enhanced with actual form analysis)
        # For now, we'll use a simple metric based on rep consistency
        form_score = min(10.0, 6.0 + (total_reps * 0.1))  # Simple scoring system
        form_score = round(form_score, 1)
        
        # Initialize database connection and workout tracker
        db_manager = DatabaseManager()
        workout_tracker = WorkoutTracker(db_manager)
        
        # Create detailed notes
        notes = f"Right arm: {st.session_state.right_rep_count} reps, Left arm: {st.session_state.left_rep_count} reps"
        
        # Save workout to database
        success = workout_tracker.log_workout(
            user_id=user_id,
            exercise_type="Bicep Curls",
            duration=duration_minutes,
            reps=total_reps,
            sets=1,  # Assuming one continuous set
            calories_burned=calories_burned,
            form_score=form_score,
            notes=notes
        )
        
        if success:
            st.session_state.workout_saved = True
            st.success(f"✅ Workout saved successfully!")
            st.info(f"📊 **Session Summary:**\n"
                   f"- Total reps: {total_reps}\n"
                   f"- Duration: {duration_minutes} minutes\n"
                   f"- Calories burned: {calories_burned}\n"
                   f"- Form score: {form_score}/10")
            return True
        else:
            st.error("❌ Failed to save workout data")
            return False
            
    except Exception as e:
        st.error(f"❌ Error saving workout: {str(e)}")
        return False

def reset_session_counters():
    """Reset all session counters and start time"""
    st.session_state.right_rep_count = 0
    st.session_state.left_rep_count = 0
    st.session_state.session_start_time = datetime.now()
    st.session_state.workout_saved = False
    st.session_state.session_active = True

def end_session():
    """End the current session and clean up"""
    st.session_state.session_active = False
    
    # Clear session state variables
    if 'right_rep_count' in st.session_state:
        del st.session_state.right_rep_count
    if 'left_rep_count' in st.session_state:
        del st.session_state.left_rep_count
    if 'session_start_time' in st.session_state:
        del st.session_state.session_start_time
    if 'workout_saved' in st.session_state:
        del st.session_state.workout_saved
    if 'session_active' in st.session_state:
        del st.session_state.session_active

def bicep_curl_tracker():
    """Main bicep curl tracking function with improved session management"""
    
    # Check if user is authenticated
    if not auth.is_authenticated():
        st.error("🔒 Please log in to use this feature.")
        if st.button("🏠 Go to Home"):
            st.switch_page("gym_webapp.py")
        return
    
    # Get user data
    user_data = auth.get_user_data()
    
    # Initialize session state
    initialize_session_state()
    
    st.title("💪 Bicep Curls Detection")
    st.markdown(f"**Welcome, {user_data['name']}!** Ready to track your bicep curls?")
    
    # Create columns for layout
    col1, col2 = st.columns([3, 1])
    
    with col2:
        # Session info
        st.markdown("### 📊 Session Info")
        
        # Calculate session duration
        current_duration = datetime.now() - st.session_state.session_start_time
        duration_minutes = int(current_duration.total_seconds() / 60)
        duration_seconds = int(current_duration.total_seconds() % 60)
        
        st.metric("Session Duration", f"{duration_minutes}:{duration_seconds:02d}")
        st.metric("Right Curls", st.session_state.right_rep_count)
        st.metric("Left Curls", st.session_state.left_rep_count)
        st.metric("Total Reps", st.session_state.right_rep_count + st.session_state.left_rep_count)
        
        st.markdown("---")
        
        # Control buttons
        col_reset, col_finish = st.columns(2)
        
        with col_reset:
            if st.button("🔄 Reset", use_container_width=True, help="Reset counters"):
                reset_session_counters()
                st.rerun()
        
        with col_finish:
            if st.button("🛑 Finish", use_container_width=True, type="primary", help="End session and save workout"):
                # Save the workout before ending session
                if not st.session_state.workout_saved:
                    if save_workout_session(user_data['id']):
                        st.success("✅ Session saved successfully!")
                        time.sleep(2)  # Give user time to see the success message
                
                # End session and redirect
                end_session()
                st.success("🏠 Redirecting to home...")
                time.sleep(1)
                st.switch_page("gym_webapp.py")
                return
        
        # Emergency stop (without saving)
        if st.button("❌ Stop Without Saving", use_container_width=True, help="End session without saving"):
            end_session()
            st.switch_page("gym_webapp.py")
            return
    
    with col1:
        st.markdown("### 📹 Live Webcam Feed")
        
        # Check if session is still active
        if not st.session_state.get('session_active', True):
            st.info("Session ended. Redirecting...")
            st.switch_page("gym_webapp.py")
            return
        
        # Video processing
        stframe = st.empty()
        
        # Try to initialize webcam
        try:
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                st.error("❌ Could not access webcam. Please check your camera permissions.")
                return
            
            # Set camera properties for better performance
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
        except Exception as e:
            st.error(f"❌ Error initializing camera: {str(e)}")
            return

        # État des bras (local variables for frame-by-frame tracking)
        right_arm_extended = True
        left_arm_extended = True

        # Définition des couleurs pour le feedback (format BGR pour OpenCV)
        COLOR_BLUE = (255, 0, 0)
        COLOR_ORANGE = (0, 165, 255)
        COLOR_GREEN = (0, 255, 0)
        COLOR_RED = (0, 0, 255)

        # Main video processing loop
        frame_count = 0
        
        # Variables for tracking arm state across frames
        right_arm_extended = True
        left_arm_extended = True
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.error("❌ Failed to capture frame from webcam.")
                break
            
            # Check if session is still active
            if not st.session_state.get('session_active', True):
                break

            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            try:
                results = pose.process(frame_rgb)
            except Exception as e:
                st.error(f"❌ Error processing pose: {str(e)}")
                break

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
                )
                landmarks = results.pose_landmarks.landmark

                try:
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
                    elif right_elbow_angle < 50:  # Adjusted threshold for better detection
                        feedback_right = "Good Right Curl!"
                        color_right = COLOR_GREEN
                        # Comptage de la répétition
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
                    elif left_elbow_angle < 50:  # Adjusted threshold for better detection
                        feedback_left = "Good Left Curl!"
                        color_left = COLOR_GREEN
                        # Comptage de la répétition
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

                    # Affichage des angles (debug info)
                    cv2.putText(
                        frame, f"R: {int(right_elbow_angle)}°", (50, 250),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
                    )
                    cv2.putText(
                        frame, f"L: {int(left_elbow_angle)}°", (50, 280),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
                    )

                    # Affichage des compteurs de répétitions
                    cv2.putText(
                        frame, f"Right Curls: {st.session_state.right_rep_count}",
                        (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2
                    )
                    cv2.putText(
                        frame, f"Left Curls: {st.session_state.left_rep_count}",
                        (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2
                    )

                except Exception as e:
                    # If there's an error processing landmarks, show error on frame
                    cv2.putText(
                        frame, "Error processing pose", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR_RED, 2
                    )

            else:
                # No pose detected
                cv2.putText(
                    frame, "No pose detected - Position yourself in view", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_RED, 2
                )

            # Update sidebar metrics every 30 frames (~once per second)
            # Note: Due to Streamlit's architecture, we'll show metrics on video frame
            # and update session_state for when user interacts with buttons
            
            # Add session info directly on the video frame for real-time feedback
            current_duration = datetime.now() - st.session_state.session_start_time
            duration_minutes = int(current_duration.total_seconds() / 60)
            duration_seconds = int(current_duration.total_seconds() % 60)
            total_reps = st.session_state.right_rep_count + st.session_state.left_rep_count
            
            # Display session info on video frame
            cv2.putText(
                frame, f"Duration: {duration_minutes}:{duration_seconds:02d}", 
                (frame.shape[1] - 300, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
            )
            cv2.putText(
                frame, f"Total Reps: {total_reps}", 
                (frame.shape[1] - 300, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
            )
            cv2.putText(
                frame, f"R: {st.session_state.right_rep_count} | L: {st.session_state.left_rep_count}", 
                (frame.shape[1] - 300, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
            )

            # Affichage de l'image dans Streamlit
            stframe.image(frame, channels="BGR", use_container_width=True)
            
            frame_count += 1
            
            # Small delay to prevent overwhelming the system
            time.sleep(0.03)  # ~30 FPS

        # Clean up
        cap.release()
        cv2.destroyAllWindows()

# Main function for the Streamlit page
def main():
    """Main function to run the bicep curl tracker"""
    st.set_page_config(
        page_title="FormFit AI - Bicep Curls",
        page_icon="💪",
        layout="wide"
    )
    
    # Apply custom CSS if available
    try:
        from style_utils import load_css
        load_css()
    except ImportError:
        pass
    
    # Run the bicep curl tracker
    bicep_curl_tracker()

if __name__ == "__main__":
    main()