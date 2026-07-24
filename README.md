# pose_estimation

单人视频 -> 可旋转 3D 骨架动画(HTML)。基于 mediapipe 提取姿态,用 plotly 生成可播放/拖拽的 3D 动画。
问题是现在没有特别适合的数据集（缺乏职业选手的姿势分析的视频）

## 安装

需要 **Python 3.9 ~ 3.12**(由 mediapipe 决定,不支持 3.13+ 或 3.8 及以下)。

推荐单独建 conda 环境:

```
conda create -n pose_estimation python=3.11 -y
conda activate pose_estimation
pip install -r requirements.txt
```

也可以在已有环境里直接安装:

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

## TODO

- 姿势评分:基于关键关节角度、躯干旋转、重心转移、随挥路径等指标,对发球、正手、反手等动作给出可解释评分。
- 标准动作对比:用 THETIS 的 expert 样本或名将短视频提取参考骨架,和用户视频做同动作阶段对齐,输出差异点。
- 动作阶段切分:自动识别准备、引拍、击球、随挥等阶段,避免只看单帧姿势。
- 多视角 3D 查看:继续强化 HTML 里的可旋转骨架视图,支持从侧面、背面、俯视等角度检查姿势,不要只依赖原视频的单一机位。
- 关键帧标记:在动画时间轴上标出疑似击球点、最大引拍点、随挥结束点,方便复盘。
- 数据集整理:下载 THETIS 后按 beginner/expert、动作类别、视频类型建立索引,便于抽样训练和评估。

## 使用 CalTennis 示例数据

项目可以直接用 [CalTennis](https://huggingface.co/datasets/demalenk/caltennis) 里的单人网球视频做验证。完整数据集较大,建议先只下载 `mini` split 里的一条视频:

```
python download_caltennis_sample.py --split mini --index 0
```

脚本会把视频下载到 `datasets/caltennis/`,并打印需要写入 [config.py](config.py) 的配置,例如:

```
VIDEO = r"datasets/caltennis/.../xxx.mp4"
POSES_NAME = "caltennis_xxx"
FORCE_REEXTRACT = False
```

改完后运行:

```
python main.py
```

如果想先看有哪些样本而不下载视频,可以只拉元数据:

```
python download_caltennis_sample.py --split mini --index 0 --metadata-only
```

## THETIS Tennis Dataset

[THETIS](https://github.com/THETIS-dataset/dataset) 是一个面向网球击球动作识别的人体动作数据集,全名是 **THree dimEnsional TennIs Shots**。它用 Kinect 采集,包含 RGB、depth、silhouette,以及部分 2D/3D skeleton 视频,适合用来验证发球、正手、反手等挥拍动作的姿态提取和动作分类流程。

数据集共有 55 个被试,其中:

- `p1` ~ `p31` 是 beginner
- `p32` ~ `p55` 是 expert

这个划分很适合做两类实验:一类是只按动作类别训练/评估,例如 forehand、backhand、service;另一类是比较 beginner 和 expert 在同一动作上的姿态差异,例如发球时躯干伸展、髋肩旋转、随挥路径等。

THETIS 包含 12 类击球动作:

- `backhand` — 单手反手
- `backhand2h` — 双手反手
- `bslice` — 反手削球
- `bvolley` — 反手截击
- `foreflat` — 平击正手
- `foreopen` — 开放式正手
- `fslice` — 正手削球
- `fvolley` — 正手截击
- `serflat` — 平击发球
- `serkick` — kick 发球
- `serslice` — slice 发球
- `smash` — 高压球

如果之后下载,建议放到 `data/thetis/`。`data/` 已加入 `.gitignore`,避免把视频数据提交进仓库。

## 文件说明

| 文件 | 作用 |
|---|---|
| `main.py` | 入口,串联提取 -> 缓存 -> 可视化 -> (可选)导出视频 |
| `config.py` | 所有配置项,改参数只需要改这里 |
| `pose_extract.py` | 视频 -> 3D 姿态序列(`extract_poses`) |
| `visualize.py` | 姿态序列 -> plotly 动画(`build_figure`),以及可选的 mp4 导出(`export_video`) |
| `check_footage.py` | 独立诊断脚本,正式提取前先摸清素材能不能支撑分析,见下文 |
| `download_caltennis_sample.py` | 从 Hugging Face 下载一条 CalTennis 样本视频 |

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
