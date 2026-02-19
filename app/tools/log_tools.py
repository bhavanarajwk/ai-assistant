from langchain_core.tools import tool

LOG_PATH = "logs/app.log"

@tool
def analyze_error_spike() -> str:
    """
    Counts total ERROR logs in the system.
    Use this tool when user asks about error increase or spike.
    """
    error_count = 0

    with open(LOG_PATH, "r") as f:
        for line in f:
            if "ERROR" in line:
                error_count += 1

    return f"Total ERROR logs found: {error_count}"
