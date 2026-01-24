import cv2
import numpy as np
import mss
import threading
import time
import os
from datetime import datetime

# ========== 固定保存路径：桌面 ==========
desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
FPS = 20  # 帧率

# ========== 录制控制 ==========
stop_flag = threading.Event()

# ========== 视频录制 ==========
def record_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # 主显示器
        width, height = monitor["width"], monitor["height"]

        # 生成带时间戳的文件名
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_video = os.path.join(desktop, f"{timestamp}.mp4")

        # 使用 mp4v 编码直接保存为 mp4
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_video, fourcc, FPS, (width, height))

        print(f"开始录制...(按 Ctrl + C 停止)\n录制文件将保存到：{output_video}")

        frame_interval = 1.0 / FPS  # 每帧之间的时间间隔
        next_frame_time = time.time()

        while not stop_flag.is_set():
            current_time = time.time()

            # 只有到达下一帧时间时才录制
            if current_time >= next_frame_time:
                img = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                out.write(frame)

                # 计算下一帧的时间
                next_frame_time += frame_interval

                # 如果落后太多，重新同步
                if current_time - next_frame_time > frame_interval:
                    next_frame_time = current_time
            else:
                # 短暂休眠，避免占用过多 CPU
                time.sleep(0.001)

        out.release()
        print(f"✅ 录制完成，文件已保存到：{output_video}")

# ========== 主程序 ==========
if __name__ == "__main__":
    video_thread = threading.Thread(target=record_screen)
    video_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止录制...")
        stop_flag.set()

    video_thread.join()
