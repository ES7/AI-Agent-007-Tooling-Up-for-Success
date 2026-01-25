import json


def load_tools_config(path="tools_config.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["tools"]


def tools_as_prompt_block(tools):
    lines = []
    for t in tools:
        lines.append(f"- tool_name: {t['tool_name']}")
        lines.append(f"  description: {t.get('description','')}")
        if t.get("arguments"):
            lines.append("  arguments:")
            for a in t["arguments"]:
                lines.append(f"    - {a['name']} ({a['type']})")
        else:
            lines.append("  arguments: []")
        lines.append("")
    return "\n".join(lines)
