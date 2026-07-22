"""
极简版:单人视频 -> 可旋转 3D 骨架 HTML
依赖: pip install -r requirements.txt
用法: 改 config.py 里的路径,然后 python main.py
"""

import os
from datetime import datetime

import numpy as np

import config
from pose_extract import extract_poses
from visualize import build_figure, export_video

os.makedirs(config.POSES_DIR, exist_ok=True)
name = config.POSES_NAME or datetime.now().strftime("%Y%m%d_%H%M%S")
poses_path = os.path.join(config.POSES_DIR, f"{name}.npy")

if config.FORCE_REEXTRACT or not os.path.exists(poses_path):
    poses = extract_poses(config.VIDEO, config.STRIDE)
    np.save(poses_path, poses)
    print(f"提取到 {len(poses)} 帧,已保存到 {poses_path}")
else:
    poses = np.load(poses_path)
    print(f"已加载缓存的 {len(poses)} 帧 (来自 {poses_path})")

if len(poses) == 0:
    raise RuntimeError(
        "没有提取到任何姿态帧,无法生成动画。"
        "可能原因:视频里没有检测到人,或缓存的 poses.npy 是空的。"
    )

fig = build_figure(poses, config.FPS)
fig.write_html(config.HTML_PATH)
print(f"完成: {config.HTML_PATH}(浏览器打开即可旋转/播放)")

if config.EXPORT_VIDEO:
    export_video(poses, config.FPS, config.VIDEO_OUT_PATH)
    print(f"完成: {config.VIDEO_OUT_PATH}")
