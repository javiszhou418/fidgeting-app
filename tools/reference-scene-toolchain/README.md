# Reference scene toolchain

Installed on 2026-08-24 for camera, material, and light matching.

## Installed components

- `arjun988/blender-skills` at `8f778d2405a214b508d4c7d80742be8e43acdd52`
- `RobLe3/cc-blender-skill` at `11016c9a5847897491dde935c346571bd7548e3d`
- `ahujasid/blender-mcp` at `2330c25c46d62b714c8106c19da0173fdeeae144`
- `stuffmatic/fSpy-Blender` at `eec40b085d45cc623fd379998d85b88de679d4b8`
- `DiffusionLight/DiffusionLight-Turbo` at `6e8b0f1ad664f5e11281d80482ae19a490927cc4`
- `DiffusionLight/DiffusionLight-Turbo-diffusers` at `ef7a372e54d5cfeeb47ae5900a5531dbc0628b56`
- `DLR-RM/BlenderProc` at `76bd8b82ee19489843578ff045298642197bf883`

Source checkouts live under:

`~/.local/share/fidgeting-scene-match/repos/`

The two skill packs expose 124 skill directories through `.cursor/skills/`.
Blender MCP is configured in `.cursor/mcp.json` with telemetry disabled.

## Native tools

- Blender `5.2.0 LTS`
- fSpy `1.0.3` at `/Applications/fSpy.app`
- BlenderProc `2.8.0` via `uv tool`
- Blender MCP and fSpy importer enabled for Blender `5.2`
- Existing `cli-anything-blender 1.0.0`

BlenderProc uses a writable Blender `4.2.1` copy at:

`~/.local/share/fidgeting-scene-match/blender/Blender-4.2.1.app`

Its macOS custom-path detection received a local two-line fix so it inspects
`Blender.app/Contents/Resources/<version>`. Reinstalling BlenderProc will require
reapplying that fix.

## DiffusionLight compatibility

The official research environment pins CUDA 11.8 and cannot run unchanged on
Apple Silicon. Its source is installed. An isolated MPS environment is at:

`~/.local/share/fidgeting-scene-match/venvs/diffusionlight-mps/`

The environment passes imports for PyTorch, MPS, Diffusers 0.33, Transformers,
OpenEXR, and OpenCV. Model weights are not pre-downloaded. The upstream
inference script still requires a reviewed CUDA-to-MPS adaptation before use.

## Verification

- 124 Cursor skill links; 0 broken links.
- Blender MCP and fSpy addons load in Blender `5.2`.
- fSpy imported its `canon5d_16mm.fspy` test camera successfully.
- DiffusionLight environment reports MPS built and available.
- BlenderProc quickstart rendered one frame on the Apple M4 Max Metal device
  and wrote `output/0.hdf5` in 34.272 seconds.
- Model-provenance tests pass `12/12`.

## Security and lifecycle

Blender MCP can execute arbitrary Python inside Blender. Keep it project-local,
leave telemetry disabled, and start only one MCP server. Cursor must restart to
load the newly registered MCP server and skills. CLIAnything and direct Blender
scripts remain available without a restart.
