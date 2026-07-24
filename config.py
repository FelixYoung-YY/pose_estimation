"""集中配置项"""

VIDEO = r"datasets\caltennis\01_23_2026_17_00_court2\01_23_2026_16_59_47_000_2_E_01_18_20_30_998.mp4"  # 改成你的视频路径
STRIDE = 5            # 每 2 帧取 1 帧,长视频可调大
FPS = 15              # 回放帧率

FORCE_REEXTRACT = False   # True: 即便同名缓存已存在,也强制重新提取并覆盖

EXPORT_VIDEO = False      # True: 额外导出 mp4(需要 pip install kaleido)
VIDEO_OUT_PATH = "skeleton.mp4"

POSES_DIR = "poses"       # 姿态缓存目录
POSES_NAME = "caltennis_01_23_2026_16_59_47_000_2_E_01_18_20_30_998"  # 缓存文件名(不含扩展名)。
                          # 指定了就按这个名字复用/覆盖缓存;
                          # 留空(None)则每次用当前时间戳命名,保证不会误加载旧数据

HTML_PATH = "skeleton.html"
