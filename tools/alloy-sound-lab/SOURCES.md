# 素材与授权

## 产品内部素材

以下 5 个文件复制自正式 Unity 产品，用于离线对比；原始文件仍以 Unity 目录为权威来源：

- `unity/FidgetingApp/Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_01.wav`
- `unity/FidgetingApp/Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_02.wav`
- `unity/FidgetingApp/Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_03.wav`
- `unity/FidgetingApp/Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_04.wav`
- `unity/FidgetingApp/Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_05.wav`

## CC0 单次击发素材

为避免“咔—嗒”两次撞击，实验台内的文件只截取原录音中的一个起音并做短淡出。授权仍归原素材页面所列许可：

- Zippo single click — [vibe_crc, `zippo_open_8shots.wav`](https://freesound.org/people/vibe_crc/sounds/47986/) — CC0
- Metal mechanism — [rottako, `metal-mechanism-click.mp3`](https://freesound.org/people/rottako/sounds/693587/) — CC0
- Resonant switch — [xkeril, `Switch metal mechanical`](https://freesound.org/people/xkeril/sounds/613918/) — CC0
- Metallic button — [BlondPanda, `Metallic_Click`](https://freesound.org/people/BlondPanda/sounds/778444/) — CC0
- Metal clink — [Breviceps, `Metallic / mechanical sound`](https://freesound.org/people/Breviceps/sounds/505669/) — CC0

## CC0 音叉与长共振素材

实验台保存了适合本地预览的 8–12 秒 MP3 摘要；合成声音会跳过原录音击打头，只读取连续尾音，因此不会产生第二次 click。

- 440 Hz resonance box — [jmuehlhans, `Tuning Fork 440 Hz, Resonance Box`](https://freesound.org/people/jmuehlhans/sounds/220747/) — CC0
- Approx. 440 Hz pickup — [jensen1, `tuningfork.wav`](https://freesound.org/people/jensen1/sounds/331038/) — CC0
- 432 Hz raw tuning fork — [FOSSarts, `Tuning fork 432Hz smack 3`](https://freesound.org/people/FOSSarts/sounds/740417/) — CC0
- Vibratone E — [xyzr_kx, `vibratone_e.wav`](https://freesound.org/people/xyzr_kx/sounds/11739/) — CC0

## 合成音叉

“合成音叉”不读取外部录音。它以一个基频和三组低电平非谐波模态实时生成连续衰减尾音；所有模态使用平滑起音包络，不创建第二个瞬态。

## 罐头币参考还原

- 参考视频：[小红书「解压罐头币！？」](https://www.xiaohongshu.com/discovery/item/6a6b44780000000025001155)，由用户在本次研究中提供。
- 页面不保存完整视频或完整原声。`xhs-can-coin-reference-press.wav` 只保留视频 21.815–23.380 秒的 1.565 秒完整按压动作，对按压前 130 ms 底噪作温和频谱扣除，并使用 82 Hz 高通、18.5 kHz 低通和短淡出。
- `scripts/extract_can_coin_press.py` 记录提取窗口与处理方法。页面直接按原始时间顺序播放这次按压，不再把另一处 Click 重复编排成滚珠/棘轮序列。
- `xhs-can-coin-pure-click.wav` 保留同一动作中 22.142 秒处的真实按压，长 116 ms；`xhs-can-coin-pure-rebound.wav` 保留 23.256 秒处手指松开时的独立真实回弹，长 94 ms。`scripts/extract_can_coin_pure_click.py --event press|rebound` 为两声分别选择无撞击背景窗，以时间/频率双向中值滤波区分音乐横向谱线与机械纵向瞬态，再执行自适应频谱扣除、155 Hz 高通、18 kHz 低通和短噪声门。回弹不复制、不移调按压声，两者之间不保留背景音乐。
- 该素材仅用于本地产品声音研究；原视频及其音频权利仍属于原作者/权利人。若用于公开发行，应先完成权利确认或以重新录制/完全合成版本替换。
