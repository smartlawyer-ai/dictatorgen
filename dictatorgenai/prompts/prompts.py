CAPABILITIES_TASK_PROMPT_SYSTEM = (
    "Your goal is to determine if the given capabilities from agents are able to solve the given task. "
    "Format the response as JSON with a result that equals 'true' or 'false' and a confidence by capability.\n"
    "If the sum of confidence is equal or greater than 1, reply with result 'true'.\n"
    "Here is an example of the expected JSON result:\n"
    "----------------------\n"
    '{\n'
    '  "result": "true",\n'
    '  "confidence_capabilities": {\n'
    '    "write_contract": "0.7",\n'
    '    "reply_with_lawcase": "0.3",\n'
    '    "speak_french": "0.9"\n'
    '  }\n'
    '}\n'
    "----------------------"
)

CAPABILITIES_TASK_PROMPT_USER = (
    "Here are the capabilities:\n"
    "-------------------------\n"
    "{capabilities_str}\n"
    "-------------------------\n"
    "Can you solve the following task: {task}?"
)
