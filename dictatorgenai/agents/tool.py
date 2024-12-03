import inspect

def tool(description: str, tool_type: str = "function"):
    """
    Decorator to mark a function as a tool and attach metadata.

    Args:
        description (str): A brief description of the tool.
        tool_type (str): The type of the tool. Default is "function".

    Returns:
        callable: The decorated function.
    """
    def decorator(func):
        func.is_tool = True
        func.tool_description = description
        func.tool_type = tool_type

        # Generate parameter schema dynamically from the function signature
        signature = inspect.signature(func)
        parameters = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

        # Map Python types to JSON Schema types
        type_mapping = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
            type(None): "null",
        }

        for name, param in signature.parameters.items():
            param_type = param.annotation
            json_type = type_mapping.get(param_type, "string")  # Default to "string" if unknown

            if param.default is param.empty:  # Required parameter
                parameters["required"].append(name)

            parameters["properties"][name] = {
                "type": json_type,
                "description": f"Argument for {name}"  # Placeholder description
            }

        func.tool_parameters = parameters

        return func
    return decorator
