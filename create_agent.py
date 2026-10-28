import os
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    BingCustomSearchPreviewTool,
    BingCustomSearchToolParameters,
    BingCustomSearchConfiguration,
)

from dotenv import load_dotenv
load_dotenv()

PROMPT = """
You are a software upgrade research agent.

Given a package name and installed version, use Bing Custom Search to find
official release notes, security advisories, and support information.

Summarize:
- Security issues affecting the installed version and available fixes.
- Whether the version is still supported.
- Relevant breaking changes and upgrade requirements.

Use only retrieved evidence and include source URLs. If applicability is
unclear, say so. Do not treat missing evidence as proof that a version is safe.

Return a JSON object with:
- package
- installed_version
- summary
- source_urls
"""

conn_id = os.getenv("CONN_ID")

project_client = AIProjectClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential()
)

tool = BingCustomSearchPreviewTool(
    bing_custom_search_preview=BingCustomSearchToolParameters(
        search_configurations=[
            BingCustomSearchConfiguration(
                project_connection_id=conn_id,
                instance_name=os.getenv("DOMAIN_NAME"),
            )
        ]
    )
)

with project_client:
    agent = project_client.agents.create_version(
        agent_name="extract-news-agent",
        definition=PromptAgentDefinition(
            model="gpt-4.1",
            instructions=PROMPT,
            tools=[tool],
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")