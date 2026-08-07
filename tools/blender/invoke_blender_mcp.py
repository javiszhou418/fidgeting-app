#!/usr/bin/env python3
"""Small MCP client used while Codex is waiting for a newly-added server reload.

The normal long-term path is the global ``blender`` MCP entry. This client uses
the exact same stdio command and environment so the current task can invoke the
server before the Codex desktop app is restarted.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


UVX = "/Users/jiawei.zhou/.local/bin/uvx"


async def run(args: argparse.Namespace) -> int:
    environment = os.environ.copy()
    environment.update(
        {
            "BLENDER_HOST": "localhost",
            "BLENDER_PORT": "9876",
            "DISABLE_TELEMETRY": "true",
        }
    )
    server = StdioServerParameters(
        command=UVX,
        args=["--python", "3.11", "blender-mcp"],
        env=environment,
    )

    async with stdio_client(server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            if args.list_tools:
                result = await session.list_tools()
                print(json.dumps([tool.model_dump() for tool in result.tools], indent=2))
                return 0
            if args.scene_info:
                result = await session.call_tool(
                    "get_scene_info",
                    {"user_prompt": "Validate the generated three-blade spinner scene hierarchy."},
                )
                print(json.dumps(result.model_dump(), indent=2, default=str))
                return 1 if result.isError else 0
            if args.tool:
                result = await session.call_tool(
                    args.tool,
                    json.loads(args.tool_args),
                )
                print(json.dumps(result.model_dump(), indent=2, default=str))
                return 1 if result.isError else 0

            source_path = Path(args.execute_file).resolve()
            code = (
                "from pathlib import Path\n"
                f"_codex_source = Path({str(source_path)!r})\n"
                "exec(compile(_codex_source.read_text(encoding='utf-8'), "
                "str(_codex_source), 'exec'))"
            )
            result = await session.call_tool(
                "execute_blender_code",
                {"code": code},
            )
            payload = result.model_dump()
            print(json.dumps(payload, indent=2, default=str))
            return 1 if result.isError else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list-tools", action="store_true")
    group.add_argument("--scene-info", action="store_true")
    group.add_argument("--execute-file")
    group.add_argument("--tool")
    parser.add_argument("--tool-args", default="{}")
    return asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
