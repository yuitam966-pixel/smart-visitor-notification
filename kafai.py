from datetime import datetime

from email.mime.image import MIMEImage  

from email.mime.multipart import MIMEMultipart  

from email.mime.text import MIMEText

import smtplib

import cv2

import numpy as np

import sounddevice as sd

import time

import threading

from flask import Flask, Response



# --- 設定項目 ---

SENDER = os.getenv("MAIL_ADDRESS")

PASSWORD = os.getenv("MAIL_PASSWORD")

THRESHOLD = 0.15 # あなたのマイクに合わせて調整した値

COOLDOWN = 15   # 動画配信（10秒）より少し長く設定



# Flaskの初期化

app = Flask(__name__)



cap = cv2.VideoCapture(0)

lock = threading.Lock()



# 状態管理のための変数

is_streaming = False

streaming_end_time = 0



def send_email_with_image(image_path):

  try:

    msg = MIMEMultipart()

    msg["Subject"] = "【スマート来客通知】来客検知通知"

    msg["From"] = SENDER

    msg["To"] = SENDER



    body = MIMEText("インターホンの音を検知しました。添付された画像を確認してください。\n現在10秒間のライブ配信中です。")

    msg.attach(body)



    with open(image_path, "rb") as f:

      img_data = f.read()

      img = MIMEImage(img_data)

      img.add_header("Content-Disposition", "attachment", filename=image_path)

      msg.attach(img)



    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

    server.login(SENDER, PASSWORD)

    server.send_message(msg)

    server.quit()

    print("➔ 画像付きメールの送信完了")

  except Exception as e:

    print(f"メール送信エラー: {e}")



# --- 音声監視処理 ---

def sound_monitor():

  global is_streaming, streaming_end_time

  print("インターホン音待機中...")

  last_detection = 0

   

  while True:

    recording = sd.rec(

      int(0.5 * 16000),

      samplerate=16000,

      channels=1

    )

    sd.wait()

     

    volume = np.std(recording)

    print(f"音量: {volume:.3f}")

     

    current_time = time.time()

     

    if volume > THRESHOLD and (current_time - last_detection > COOLDOWN):

      print("★大きな音を検知！10秒間の動画配信を開始します★")

       

      # 10秒間だけ配信フラグをONにする

      is_streaming = True

      streaming_end_time = current_time + 10

       

      with lock:

        ret, frame = cap.read()

       

      if ret:

        filename = datetime.now().strftime("visitor_%Y%m%d_%H%M%S.jpg")

        cv2.imwrite(filename, frame)

        print("画像保存:", filename)

         

        # メール送信は裏で並行して行う（動画配信が遅れないようにするため）

        email_thread = threading.Thread(target=send_email_with_image, args=(filename,))

        email_thread.start()

         

      last_detection = current_time



# --- WEB動画ストリーミング処理 ---

def generate_frames():

  global is_streaming

  while True:

    current_time = time.time()

     

    # 音を検知した時間内（10秒間）だけ映像を送る

    if is_streaming and current_time < streaming_end_time:

      with lock:

        ret, frame = cap.read()

      if not ret:

        break

      ret, buffer = cv2.imencode('.jpg', frame)

      frame_bytes = buffer.tobytes()

      yield (b'--frame\r\n'

          b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

      time.sleep(0.04)

    else:

      # 10秒過ぎたらフラグをオフにして、待機中画像を出すか少し待つ

      is_streaming = False

      # 黒い画面（または案内文字）をブラウザに送って停止状態にする

      blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)

      cv2.putText(blank_frame, "Waiting for sound...", (140, 240), 

            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

      ret, buffer = cv2.imencode('.jpg', blank_frame)

      yield (b'--frame\r\n'

          b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

      time.sleep(1)



@app.route('/video_feed')

def video_feed():

  return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/')

def index():

  return """

  <h1>スマート来客通知システム ライブカメラ</h1>

  <p>音を検知すると、ここに10秒間リアルタイム映像が映ります。</p>

  <img src='/video_feed' width='640'>

  """



if __name__ == "__main__":

  print("システム起動")

  monitor_thread = threading.Thread(target=sound_monitor, daemon=True)

  monitor_thread.start()

  app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)