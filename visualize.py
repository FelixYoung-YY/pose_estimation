"""3D 姿态 -> 可旋转动画 HTML"""

import numpy as np
import plotly.graph_objects as go
from tqdm import tqdm

from pose_extract import CONN


def traces(p):
    x, y, z = p[:, 0], -p[:, 2], -p[:, 1]        # 调整轴向让人直立
    lx, ly, lz = [], [], []
    for a, b in CONN:
        lx += [x[a], x[b], None]; ly += [y[a], y[b], None]; lz += [z[a], z[b], None]
    return [go.Scatter3d(x=x, y=y, z=z, mode="markers", marker=dict(size=4)),
            go.Scatter3d(x=lx, y=ly, z=lz, mode="lines", line=dict(width=5))]


def export_video(poses, fps, out_path):
    """把动画渲染成 mp4(需要 pip install kaleido)。逐帧调用 kaleido 渲染 PNG,帧数多会比较慢。"""
    import cv2

    r = np.abs(poses).max() * 1.1
    axis = dict(range=[-r, r], showbackground=False)
    writer = None
    for p in tqdm(poses, desc="导出视频", unit="帧"):
        frame_fig = go.Figure(data=traces(p))
        frame_fig.update_layout(
            scene=dict(xaxis=axis, yaxis=axis, zaxis=axis, aspectmode="cube"),
            showlegend=False, width=800, height=800,
        )
        img = cv2.imdecode(np.frombuffer(frame_fig.to_image(format="png"), np.uint8), cv2.IMREAD_COLOR)
        if writer is None:
            h, w = img.shape[:2]
            writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
        writer.write(img)
    writer.release()


def build_figure(poses, fps):
    r = np.abs(poses).max() * 1.1
    axis = dict(range=[-r, r], showbackground=False)
    frames = [go.Frame(data=traces(p), name=str(k)) for k, p in enumerate(poses)]

    fig = go.Figure(data=frames[0].data, frames=frames)
    fig.update_layout(
        scene=dict(xaxis=axis, yaxis=axis, zaxis=axis, aspectmode="cube"),
        showlegend=False,
        updatemenus=[dict(type="buttons", buttons=[
            dict(label="播放", method="animate",
                 args=[None, dict(frame=dict(duration=1000 / fps, redraw=True), fromcurrent=True)]),
            dict(label="暂停", method="animate", args=[[None], dict(mode="immediate")])])],
        sliders=[dict(steps=[dict(method="animate", label=f.name,
                                  args=[[f.name], dict(mode="immediate", frame=dict(redraw=True))])
                             for f in frames])],
    )
    return fig
