# 📷 Smart Visitor Notification System

A smart visitor notification system developed using Raspberry Pi 5, Python, OpenCV, and Flask.

When the system detects a doorbell sound, it automatically captures a photo of the visitor, sends the image via Gmail, and starts a 10-second live video stream. The project was developed to improve home security and allow users to check visitors remotely.

---

## 📖 Overview

Many people experience situations such as:

- Being unable to identify visitors while away from home.
- Feeling concerned about security when living alone.
- Wanting to know who rang the doorbell before opening the door.

This project addresses these issues by automatically notifying the user whenever a visitor is detected.

---

## ✨ Features

- 🔊 Doorbell sound detection
- 📷 Automatic image capture
- ✉️ Email notification with attached photo
- 🌐 10-second live video streaming using Flask
- ⚡ Parallel processing using Python threads

---

## 🛠 Technologies

- Python
- OpenCV
- Flask
- Raspberry Pi 5
- NumPy
- Gmail SMTP

---

## ⚙️ System Flow

```
Visitor
   │
   ▼
Doorbell Sound Detection
   │
   ▼
Capture Image
   │
   ├──► Send Email
   │
   └──► Start Live Video Stream (10 seconds)
```

---

## 📸 Project Demo

The presentation slides included in this repository explain:

- Project background
- System configuration
- Program implementation
- Execution results
- Future improvements

---

## 💡 Future Improvements

- AI-based doorbell sound recognition
- Smartphone push notifications
- Cloud storage for captured images
- Visitor face recognition

---

## 👩‍💻 Author

Developed as a university project.
