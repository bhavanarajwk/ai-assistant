import sys
import os

sys.path.append(os.path.abspath("."))

from app.agent.incident_agent import create_agent, run_agent

agent = create_agent()

response = run_agent(
    agent,
    "Did errors increase after deployment?"
)

print("\nFinal Response:\n")
print(response)
