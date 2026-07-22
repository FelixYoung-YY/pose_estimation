# pose_estimation

单人视频 -> 可旋转 3D 骨架动画(HTML)。基于 mediapipe 提取姿态,用 plotly 生成可播放/拖拽的 3D 动画。

## 安装

需要 **Python 3.9 ~ 3.12**(由 mediapipe 决定,不支持 3.13+ 或 3.8 及以下)。

```
pip install -r requirements.txt
```

可选依赖(按需安装):

- `kaleido` — 开启 `EXPORT_VIDEO` 导出 mp4 时需要
- `librosa` — `check_footage.py` 的音频击球点检测需要(还需系统装好 ffmpeg)

## 快速开始

1. 把视频放到项目目录下(或记下完整路径)
2. 改 [config.py](config.py) 里的 `VIDEO` 指向你的视频
3. 运行

```
python main.py
```

跑完会生成 `skeleton.html`,浏览器打开即可旋转视角、拖动进度条、播放/暂停。

## 文件说明

| 文件 | 作用 |
|---|---|
| `main.py` | 入口,串联提取 -> 缓存 -> 可视化 -> (可选)导出视频 |
| `config.py` | 所有配置项,改参数只需要改这里 |
| `pose_extract.py` | 视频 -> 3D 姿态序列(`extract_poses`) |
| `visualize.py` | 姿态序列 -> plotly 动画(`build_figure`),以及可选的 mp4 导出(`export_video`) |
| `check_footage.py` | 独立诊断脚本,正式提取前先摸清素材能不能支撑分析,见下文 |

## 配置项([config.py](config.py))

- `VIDEO` — 输入视频路径
- `STRIDE` — 每几帧取一帧,长视频调大能加速,但会丢失快速动作细节
- `FPS` — 生成动画的回放帧率
- `FORCE_REEXTRACT` — 为 `True` 时忽略已有缓存,强制重新提取并覆盖
- `POSES_DIR` / `POSES_NAME` — 姿态缓存位置。`POSES_NAME` 留空(`None`)时每次用时间戳命名,保证不会误加载旧数据;想复用某次结果就显式填一个名字,同名才会命中缓存(换视频记得换名字,避免张冠李戴)
- `EXPORT_VIDEO` / `VIDEO_OUT_PATH` — 是否额外导出 mp4,以及导出路径
- `HTML_PATH` — 输出的动画 HTML 路径

## 素材诊断(挥拍类动作)

正式跑 3D 提取前,建议先用 `check_footage.py` 摸清素材帧率、模糊程度,以及用音频找到的击球点:

```
python check_footage.py your_video.mp4
```

帧率决定了能测什么、测不出什么(粗略分界):

- **≥120fps** — 挥拍主体动作 + impact 瞬间都能做定量分析
- **60fps** — 准备期/转体/随挥的大结构能看,impact 附近要谨慎解读
- **30fps 左右**(多数比赛录像/普通拍摄)— impact 前后的爆发段(约 50ms)信息在采集时已丢失,换什么模型都补不回来;但引拍、重心转移、随挥减速等慢相位持续几百毫秒,30fps 下仍有十几帧,可以做结构和时序上的定量对比

结论:素材帧率低时,把分析目标从"测击球瞬间"转向"测动作结构与时序",而不是硬测一个不可信的数字。

## 已知限制

- 目前只支持单人视频(多人场景 mediapipe Pose 只会取一个人)
- `export_video` 逐帧调用 kaleido 渲染,帧数多会比较慢
