import os

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from typesafe_sdk import TypeSafeClient

load_dotenv()

ENDPOINT = os.getenv("ENDPOINT")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
def assess_upgrade(state: str):
    with DefaultAzureCredential() as credential:
        token_provider = get_bearer_token_provider(
            credential, "https://ai.azure.com/.default"
        )

        with TypeSafeClient(
            api_key=token_provider(),
            base_url=ENDPOINT,
            model=DEPLOYMENT_NAME,
            timeout=60,
        ) as client:
            return client.system_one(
                state=state,
                questions={
                    "upgrade_needed": {
                        "type": "noul",
                        "instructions": (
                            "Does the supplied evidence indicate that the installed "
                            "version needs an upgrade? Use only the supplied evidence. "
                            "Missing evidence is not proof that no upgrade is needed."
                        ),
                        "criteria": {
                            "true": (
                                "Evidence identifies an applicable security fix, "
                                "end-of-support, or required compatibility upgrade."
                            ),
                            "false": (
                                "Evidence establishes that the installed version is "
                                "supported and no applicable upgrade requirement exists."
                            ),
                        },
                    },
                    "reason": {
                        "type": "choice",
                        "instructions": (
                            "Choose the primary upgrade reason. If multiple apply, "
                            "prioritize security-fix, then end-of-support, then "
                            "compatibility. Choose insufficient-evidence if the "
                            "installed version cannot be assessed reliably."
                        ),
                        "criteria": {
                            "security-fix": (
                                "An official advisory explicitly affects the installed "
                                "version and identifies a fix."
                            ),
                            "end-of-support": (
                                "The installed version no longer receives support."
                            ),
                            "compatibility": (
                                "An upgrade is required for the stated environment "
                                "or application requirements."
                            ),
                            "routine-update": (
                                "Only optional improvements or routine fixes apply."
                            ),
                            "no-upgrade-needed": (
                                "Evidence supports retaining the installed version."
                            ),
                            "insufficient-evidence": (
                                "Evidence is missing, conflicting, or does not "
                                "establish applicability to the installed version."
                            ),
                        },
                    },
                    "urgency": {
                        "type": "score",
                        "instructions": (
                            "Rate upgrade urgency using only verified applicability "
                            "and impact in the supplied evidence. Do not assume an "
                            "older version is vulnerable."
                        ),
                        "criteria": [
                            "Routine: no established urgent upgrade requirement.",
                            "Planned: upgrade in a normal maintenance cycle.",
                            "Urgent: applicable material security risk, unsupported "
                            "version, or significant compatibility impact.",
                            "Immediate: confirmed exposure to a critical issue or "
                            "active exploitation relevant to the stated deployment.",
                        ],
                    },
                },
            )


def print_upgrade_decision(response):
    needed = response.nouls["upgrade_needed"]
    reason = response.choices["reason"]
    urgency = response.scores["urgency"]

    print(f"Upgrade-needed signal: {needed.noul:.1%}")
    print(f"Reason: {reason.choice} (confidence: {reason.confidence:.1%})")

    if reason.choice == "insufficient-evidence":
        print("Urgency: not actionable without more evidence")
        action = "gather more evidence"
    else:
        print(f"Urgency: {urgency.score:.2f} of 3")
        if needed.noul >= 0.5 and urgency.score >= 2:
            action = "prioritize upgrade review"
        elif needed.noul >= 0.5 or reason.choice != "no-upgrade-needed":
            action = "schedule upgrade review"
        else:
            action = "monitor"

    print(f"Action: {action}")