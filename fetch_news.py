from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from model import assess_upgrade, print_upgrade_decision
import json
import os

from dotenv import load_dotenv
load_dotenv()

endpoint = os.environ["PROJECT_ENDPOINT"]
agent_name = "extract-news-agent"
user_message = "We use Django 4.2.0. Find official security advisories affecting this version and identify the fixed versions."

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=endpoint,
        credential=credential,
        allow_preview=True,
    ) as project_client,
):
    # Bind the OpenAI client to the existing agent endpoint.
    openai_client = project_client.get_openai_client(agent_name=agent_name)

    # GitHub Copilot preview agents require a conversation for every Responses turn.
    conversation = openai_client.conversations.create()
    response = openai_client.responses.create(
        conversation=conversation.id,
        input=[{"role": "user", "content": user_message}],
    )

    raw_output = response.output[-1].content[0].text
    print(raw_output)
    news_item = json.loads(raw_output)
    summary = news_item["summary"]

    # Classify each news summary
    decision = assess_upgrade(summary)
    # print(f"\nNews Summary: {summary}")
    print_upgrade_decision(decision)