# 🏋️‍♀️ FormFit – AI-Powered Gym Form Correction  

📌 **Prevent Injuries | Improve Gym Performance | Train Smarter**  

## 🚀 Problem Statement (Hackathon Track 1: Healthcare)  

Gym intimidation and fear of injury deter many, especially beginners, from exercising. Anxiety about judgement & lack of guidance create barriers to fitness, impacting both physical and mental well-being.

✅ **Remote health monitoring** – AI tracks gym posture without wearables.  
✅ **Intelligent alerts** – Detects incorrect form & prevents injury risks.  
✅ **Lifestyle management** – Encourages proper movement habits for long-term health.  

## 🛠️ Tech Stack  

| **Category**           | **Technology Used**  |
|-----------------------|--------------------|
| **Programming**        | Python |
| **Computer Vision**    | OpenCV, Mediapipe |
| **Web Framework**      | Streamlit |
| **Pose Estimation**    | Mediapipe (33 body landmarks) |
| **Mathematical Calculations** | NumPy, Trigonometry for joint angles |

---

## 📌 Features  

- **AI-Powered Real-Time Posture Tracking** – Uses a webcam to monitor exercise form.  
- **Automated Rep Counting** – Ensures users complete full, valid movements.  
- **Posture Analysis & Feedback** – Real-time detection of incorrect form & provides reminder messages accordingly.  
- **Multi-Exercise Support** – Tracks common gym exercises:  

✅ **Squats**  
✅ **Deadlifts**  
✅ **Shoulder Press**  
✅ **Bicep Curls**  
✅ **Wall Sits**  

---
## 🚀 How to Run Locally

### 1️⃣ Prerequisites
- Python 3.10
- An available webcam

### 2️⃣ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/KarrayAziz/SenecaHacks2.git
    cd Team-ALT
    ```

2.  **Create and activate a virtual environment (Recommended):**
    *   On macOS / Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install the required libraries:**
    *(Make sure you have a `requirements.txt` file in your project. If not, create one by running `pip freeze > requirements.txt`)*
    ```bash
    pip install -r requirements.txt
