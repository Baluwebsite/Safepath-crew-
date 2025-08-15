# Driver Safety Monitoring System

A real-time driver safety monitoring system using Python and OpenCV for liveness detection (blink + motion), alerting, and face/eye recognition. Built for a hackathon.

## Features

- Real-time face and eye detection with Haar cascade classifiers
- Two-factor liveness detection (blink and motion monitoring)
- Alerts for camera block, missing driver, and static image (using sound and status indicators)
- Event logging with timestamps for safety incidents
- Configurable detection parameters and thresholds
- Threading for non-blocking audio alerts

## Technology Stack

- Python
- OpenCV
- Haar Cascade Classifiers
- threading (Python standard library)
- winsound (Windows alerts)
  
## Architecture

Webcam Input Module: Initializes and captures real-time video stream for face and eye monitoring.

Face & Eye Detection Module: Utilizes Haar cascades to detect and track facial features.

Liveness & Anomaly Detection: Monitors blink rates, face movement patterns, and other safety signals.

Alert & Logging System: Issues sound alerts and maintains logs when safety thresholds are crossed (e.g., driver inattentiveness or camera obstruction).

Display/Status Module: Continuously updates the display window with real-time safety status and logs.

## Block Diagram
 Webcam Input
     ↓
Face Detection Module
     ↓
Eye Detection Module
     ↓
Blink Monitoring
     ↓
Head Movement Tracking
     ↓
Liveness Detection
     ↓
Anomaly Detection
     ↓
Alert & Logging System
     ↓
Display Output with Real-time Status


## Installation

1. **Clone the repository**
git clone https://github.com/Baluwebsite/Safepath-crew-
cd Safepath-crew
3. **Install Python dependencies**
pip install opencv-python numpy
4. Make sure your webcam is working and you are running Windows (for sound alerts).

## Usage
1. Run the main script:
                 python "final project.py"
2. The webcam will activate for monitoring.  
3. Alerts and logs will trigger if liveness fails or anomalies are detected.  
4. Press `q` to exit the program at any time.

## Project Flow

- Captures video stream from webcam
- Detects face and eyes using Haar cascades
- Monitors blink patterns and face movement
- Sounds alerts and logs incidents if safety threshold is breached
- Provides real-time status on the display window

## Example Output

<img width="1920" height="340" alt="Screenshot (61)" src="https://github.com/user-attachments/assets/579eb523-e99e-4189-93f9-182b9b4fb810" />
<img width="1920" height="347" alt="Screenshot (62)" src="https://github.com/user-attachments/assets/08484aa1-0625-4a60-aaac-b0f5118b4a77" />
<img width="1920" height="1080" alt="Screenshot (63)" src="https://github.com/user-attachments/assets/7e94367d-73fb-49bc-a481-a0abc3538116" />




## Contributing

Contributions, suggestions, and bug reports are welcome.  
Feel free to fork, create issues, or submit pull requests.

## License

This project is licensed under the MIT License.

## Acknowledgments

- For organizing the hackathon
- OpenCV community and documentation
- Hackathon participants and mentors
  


