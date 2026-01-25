import argparse
import json
from openai import OpenAI

from tools import load_tools_config
from planner import plan_with_openai
from memory import load_memory, update_memory, clear_memory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, required=True)
    parser.add_argument("--tools", type=str, default="tools_config.json")
    parser.add_argument("--model", type=str, default="gpt-4o-mini")
    parser.add_argument("--clear", action="store_true", help="Clear conversation memory")
    args = parser.parse_args()

    if args.clear:
        clear_memory()
        print("Memory cleared.")
        return

    tools = load_tools_config(args.tools)
    memory = load_memory()

    client = OpenAI()
    plan = plan_with_openai(client, args.query, tools, memory=memory, model=args.model)

    print(json.dumps(plan, indent=2))

    update_memory(args.query, plan)


if __name__ == "__main__":
    main()
