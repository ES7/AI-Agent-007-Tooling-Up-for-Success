import json

from tools import tools_as_prompt_block
from validator import safe_json_load, validate_plan, ValidationError


SYSTEM_PROMPT = """You are a tool-planning agent.
Your job: given a user query and available tools, output ONLY a JSON array of tool calls.
Do not explain anything.
Do not output markdown.
If the query cannot be solved using the tools, output [].

Output rules:
- Output must be valid JSON.
- Output must be a JSON array.
- Each element must be an object with:
  - "tool_name": string
  - "arguments": array
- Each argument must be:
  {"argument_name": "<string>", "argument_value": <any valid JSON>}
- argument_value can be string, number, boolean, list, object, or "$$PREV[i]".
- To reference the output of the ith previous tool call, use "$$PREV[i]".
- i must be less than the current tool index.

Allowed values:
- issue.priority allowed: ["p0","p1","p2","p3"] (lowercase)

IMPORTANT:
If the query is solvable using the tools, DO NOT return [].

Examples:

User Query: "What is the meaning of life?"
Output:
[]

User Query: "Summarize issues similar to don:core:dvrv-us-1:devo/0:issue/1"
Output:
[
  {
    "tool_name": "get_similar_work_items",
    "arguments": [
      {"argument_name": "work_id", "argument_value": "don:core:dvrv-us-1:devo/0:issue/1"}
    ]
  },
  {
    "tool_name": "summarize_objects",
    "arguments": [
      {"argument_name": "objects", "argument_value": "$$PREV[0]"}
    ]
  }
]

User Query: "Prioritize my P0 issues and add them to the current sprint"
Output:
[
  {"tool_name": "who_am_i", "arguments": []},
  {
    "tool_name": "works_list",
    "arguments": [
      {"argument_name": "issue.priority", "argument_value": ["p0"]},
      {"argument_name": "owned_by", "argument_value": ["$$PREV[0]"]}
    ]
  },
  {
    "tool_name": "prioritize_objects",
    "arguments": [
      {"argument_name": "objects", "argument_value": "$$PREV[1]"}
    ]
  },
  {"tool_name": "get_sprint_id", "arguments": []},
  {
    "tool_name": "add_work_items_to_sprint",
    "arguments": [
      {"argument_name": "work_ids", "argument_value": "$$PREV[2]"},
      {"argument_name": "sprint_id", "argument_value": "$$PREV[3]"}
    ]
  }
]
"""


def build_user_prompt(query, tools, memory=None):
    tool_block = tools_as_prompt_block(tools)

    memory_block = ""
    if memory and memory.get("last_query") and memory.get("last_plan") is not None:
        memory_block = f"""
Conversation context (previous turn):
Previous user query:
{memory["last_query"]}

Previous tool plan output:
{json.dumps(memory["last_plan"], indent=2)}
"""

    return f"""Available tools:
{tool_block}
{memory_block}

User query:
{query}

Return ONLY the JSON array:"""


def plan_with_openai(client, query, tools, memory=None, model="gpt-4o-mini", max_retries=3):
    last_error = None

    for attempt in range(max_retries):
        user_prompt = build_user_prompt(query, tools, memory=memory)

        if last_error:
            user_prompt += (
                "\n\nYour previous output was invalid. Fix it.\n"
                f"Validation error:\n{last_error}\n"
            )

        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )

        raw = resp.choices[0].message.content.strip()

        try:
            plan = safe_json_load(raw)
            validate_plan(plan, tools)
            return plan
        except ValidationError as e:
            last_error = str(e)

    raise RuntimeError(
        f"Failed to produce a valid plan after {max_retries} tries.\nLast error: {last_error}"
    )
