import cv2
import mediapipe as mp
import RPi.GPIO as GPIO
import requests
from datetime import datetime
tik = None
URL = 'https://prod-09.eastasia.logic.azure.com:443/workflows/6f27ab8217af45bf9b68bcfc434f15c0/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=lTtyIHc405wzEfmr8JYVVb4s0sm483mTKvbxX8gSRGc'

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

GPIO.setmode(GPIO.BOARD)
GPIO.setup(37, GPIO.OUT)

# For webcam input:
cap = cv2.VideoCapture(0)
with mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as pose:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image)

    # Draw the pose annotation on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    mp_drawing.draw_landmarks(
        image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
    # Flip the image horizontally for a selfie-view display.
    image = cv2.flip(image, 1)
    if results.pose_landmarks!=None:
      cv2.putText(image,'Someone in the car!', (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
      GPIO.output(37, GPIO.HIGH)
      #Todo:
      #email
      if tik == None or (datetime.now()-tik).total_seconds()/60 > 100: #100 mins
        tik = datetime.now()
        requests.post(URL, json={'message':'test'})
        print('sending...')
        
    
    else:
      GPIO.output(37, GPIO.LOW)
    cv2.imshow('MediaPipe Pose',image)
    if cv2.waitKey(5) & 0xFF == 27:
      GPIO.cleanup()
      break
cap.release()
GPIO.cleanup()
