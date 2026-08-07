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
