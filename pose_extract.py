"""视频 -> 3D 姿态提取"""

import numpy as np
import cv2
import mediapipe as mp
from tqdm import tqdm

CONN = list(mp.solutions.pose.POSE_CONNECTIONS)


def extract_poses(video_path, stride):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"打不开视频: {video_path}")
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or None  # 部分容器格式取不到总帧数,交给 tqdm 显示已处理数
    poses = []
    with mp.solutions.pose.Pose(model_complexity=1, smooth_landmarks=True) as pose:
        i = 0
        with tqdm(total=total, desc="提取姿态", unit="帧") as bar:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                if i % stride == 0:
                    res = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    if res.pose_world_landmarks:
                        poses.append([[l.x, l.y, l.z] for l in res.pose_world_landmarks.landmark])
                i += 1
                bar.update(1)
    cap.release()
    return np.array(poses)          # (N, 33, 3)
