"""
挥拍类运动素材诊断:先摸清素材能支撑什么样的分析,再决定模型和指标

依赖:
    pip install opencv-python numpy
    pip install librosa        # 可选,用于音频找击球点(需要 ffmpeg)

用法:
    python check_footage.py your_video.mp4
"""

import sys
import numpy as np
import cv2


def probe_basic(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise FileNotFoundError(f"打不开: {path}")
    info = dict(
        fps=cap.get(cv2.CAP_PROP_FPS),
        n_frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
    )
    info["duration"] = info["n_frames"] / info["fps"] if info["fps"] else 0
    cap.release()
    return info


def blur_profile(path, max_samples=400):
    """
    用 Laplacian 方差衡量每帧清晰度。数值越低越模糊。
    挥拍瞬间通常是全片最模糊的地方 —— 这正是我们最想看清的地方,
    所以这个指标能直观暴露采集端的损失。
    """
    cap = cv2.VideoCapture(path)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(1, n // max_samples)
    scores, idxs = [], []
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if i % step == 0:
            g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            g = cv2.resize(g, (480, int(480 * g.shape[0] / g.shape[1])))
            scores.append(cv2.Laplacian(g, cv2.CV_64F).var())
            idxs.append(i)
        i += 1
    cap.release()
    return np.array(idxs), np.array(scores)


def audio_impacts(path, fps):
    """
    击球声在音频里是极尖锐的瞬态,比视觉找 impact 更准也更省事。
    返回候选击球时刻(秒)。
    """
    try:
        import librosa
    except ImportError:
        return None, "未安装 librosa,跳过音频检测(pip install librosa)"
    try:
        y, sr = librosa.load(path, sr=None, mono=True)
    except Exception as e:
        return None, f"读音频失败(可能缺 ffmpeg 或视频无音轨): {e}"

    onset = librosa.onset.onset_detect(
        y=y, sr=sr, units="time",
        backtrack=False, pre_max=20, post_max=20,
        pre_avg=100, post_avg=100, delta=0.3, wait=30,
    )
    return np.array(onset), None


def verdict(fps, blur_scores):
    print("\n" + "=" * 52)
    print("判断")
    print("=" * 52)

    if fps >= 200:
        print(f"帧率 {fps:.0f}fps —— 很好。impact 前后采样充足,")
        print("  前臂旋内、拍头轨迹这类高速细节都可以做定量分析。")
    elif fps >= 100:
        print(f"帧率 {fps:.0f}fps —— 够用。挥拍主体动作(引拍/转体/随挥)")
        print("  可以可靠分析;impact 那一两帧仍可能被跳过,谨慎解读。")
    elif fps >= 50:
        print(f"帧率 {fps:.0f}fps —— 受限。准备期、转体、随挥的结构性对比可行;")
        print("  击球瞬间的关节角度不建议拿来做定量结论。")
    else:
        print(f"帧率 {fps:.0f}fps —— 偏低。整个挥拍加速段可能只有 2-3 帧,")
        print("  且大概率有运动模糊。建议:")
        print("    · 把分析目标从「击球瞬间」转向「动作结构与时序」")
        print("      (准备姿势、重心转移、髋肩分离建立、随挥减速、落地)")
        print("    · 这些慢相位在 30fps 下仍有十几帧,完全可以定量对比")
        print("    · 换 MotionBERT 等模型能改善 Z 轴抖动,但补不回丢失的帧")

    if len(blur_scores) > 0:
        lo, med = np.percentile(blur_scores, 5), np.median(blur_scores)
        ratio = lo / med if med > 0 else 1
        print(f"\n清晰度:中位 {med:.0f},最模糊 5% 分位 {lo:.0f}(比值 {ratio:.2f})")
        if ratio < 0.4:
            print("  → 存在明显运动模糊帧。这些帧上的关键点会飘,")
            print("     做曲线对比时建议把它们标出来或剔除。")
        else:
            print("  → 模糊程度尚可,没有出现极端糊帧。")


def main():
    if len(sys.argv) < 2:
        print("用法: python check_footage.py your_video.mp4")
        return
    path = sys.argv[1]

    info = probe_basic(path)
    print("=" * 52)
    print("素材基本信息")
    print("=" * 52)
    print(f"分辨率 : {info['width']}x{info['height']}")
    print(f"帧率   : {info['fps']:.1f} fps")
    print(f"总帧数 : {info['n_frames']}  (约 {info['duration']:.1f} 秒)")

    print("\n分析清晰度分布中……")
    idxs, scores = blur_profile(path)
    if len(scores):
        worst = idxs[np.argsort(scores)[:5]]
        print(f"最模糊的几帧位于: {sorted(worst.tolist())}")
        print("(挥拍瞬间通常就在这些帧附近)")

    print("\n用音频寻找击球点……")
    onsets, err = audio_impacts(path, info["fps"])
    if err:
        print(f"  {err}")
    elif onsets is None or len(onsets) == 0:
        print("  没找到明显的瞬态峰值(可能无音轨或环境噪声大)")
    else:
        print(f"  找到 {len(onsets)} 个候选击球时刻(秒):")
        print(f"  {np.round(onsets[:12], 2).tolist()}{' ...' if len(onsets) > 12 else ''}")
        f = info["fps"]
        print(f"  对应帧号: {[int(t * f) for t in onsets[:12]]}")
        print("  → 这些帧号可作为后续「对齐窗口」的锚点")

    verdict(info["fps"], scores)


if __name__ == "__main__":
    main()
