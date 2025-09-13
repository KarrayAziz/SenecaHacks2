# pose_utils.py
import mediapipe as mp
import numpy as np
import math

# --- Initialisation de MediaPipe Pose (une seule fois) ---
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# --- Fonction de calcul d'angle (partagée) ---
def calculate_angle(a, b, c):
    """Calcule l'angle entre trois points."""
    a = np.array(a)  # Premier point
    b = np.array(b)  # Point du milieu (sommet de l'angle)
    c = np.array(c)  # Troisième point

    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    angle = abs(radians * 180.0 / np.pi)

    return 360 - angle if angle > 180 else angle