import json
import re

PREV_PATTERN = re.compile(r"^\$\$PREV\[(\d+)\]$")


class ValidationError(Exception):
    pass


def _check_prev_reference(value, step_index):
    if isinstance(value, str):
        m = PREV_PATTERN.match(value.strip())
        if m:
            ref_index = int(m.group(1))
            if ref_index >= step_index:
                raise ValidationError(
                    f"Step {step_index}: Invalid $$PREV reference '{value}'. Must refer to earlier step."
                )


def _matches_type(value, expected_type):
    if expected_type == "string":
        return isinstance(value, str)

    if expected_type == "int":
        return isinstance(value, int) and not isinstance(value, bool)

    if expected_type == "bool":
        return isinstance(value, bool)

    if expected_type.startswith("array[") and expected_type.endswith("]"):
        if not isinstance(value, list):
            return False

        inner = expected_type[len("array["):-1]

        if inner == "string":
            return all(isinstance(x, str) for x in value)

        if inner == "object":
            return all(isinstance(x, dict) for x in value)

        return True

    return True


def validate_plan(plan, tools):
    if not isinstance(plan, list):
        raise ValidationError("Output must be a JSON array (list).")

    tool_map = {t["tool_name"]: t for t in tools}

    for i, step in enumerate(plan):
        if not isinstance(step, dict):
            raise ValidationError(f"Step {i} must be a JSON object.")

        if "tool_name" not in step or "arguments" not in step:
            raise ValidationError(f"Step {i} must contain 'tool_name' and 'arguments'.")

        tool_name = step["tool_name"]
        args = step["arguments"]

        if not isinstance(tool_name, str):
            raise ValidationError(f"Step {i}: tool_name must be a string.")

        if tool_name not in tool_map:
            raise ValidationError(f"Step {i}: Unknown tool_name '{tool_name}'.")

        if not isinstance(args, list):
            raise ValidationError(f"Step {i}: arguments must be an array (list).")

        tool_args_schema = tool_map[tool_name].get("arguments", [])
        allowed_args = {a["name"]: a["type"] for a in tool_args_schema}

        if len(allowed_args) == 0 and len(args) > 0:
            raise ValidationError(
                f"Step {i}: Tool '{tool_name}' does not take arguments, but arguments were provided."
            )

        seen_arg_names = set()

        for j, arg in enumerate(args):
            if not isinstance(arg, dict):
                raise ValidationError(f"Step {i}, argument {j}: must be a JSON object.")

            if "argument_name" not in arg or "argument_value" not in arg:
                raise ValidationError(
                    f"Step {i}, argument {j}: must contain 'argument_name' and 'argument_value'."
                )

            arg_name = arg["argument_name"]
            arg_value = arg["argument_value"]

            if not isinstance(arg_name, str):
                raise ValidationError(f"Step {i}, argument {j}: argument_name must be a string.")

            if arg_value is None:
                raise ValidationError(f"Step {i}, argument {j}: argument_value cannot be null.")

            if arg_name in seen_arg_names:
                raise ValidationError(
                    f"Step {i}: Duplicate argument_name '{arg_name}' in tool '{tool_name}'."
                )
            seen_arg_names.add(arg_name)

            if allowed_args and arg_name not in allowed_args:
                raise ValidationError(
                    f"Step {i}: Invalid argument_name '{arg_name}' for tool '{tool_name}'. "
                    f"Allowed: {sorted(list(allowed_args.keys()))}"
                )

            expected_type = allowed_args.get(arg_name)
            if expected_type and not _matches_type(arg_value, expected_type):
                raise ValidationError(
                    f"Step {i}, argument {j}: '{arg_name}' expects type '{expected_type}' "
                    f"but got '{type(arg_value).__name__}'. Value: {arg_value}"
                )

            _check_prev_reference(arg_value, i)

            if isinstance(arg_value, list):
                for item in arg_value:
                    _check_prev_reference(item, i)

    return True


def safe_json_load(text):
    try:
        return json.loads(text)
    except Exception as e:
        raise ValidationError(f"Invalid JSON output: {e}")
