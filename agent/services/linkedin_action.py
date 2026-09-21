"""LinkedIn Action Service enforcing strict Human-Approved sending and direct deep-linking."""

import urllib.parse
from typing import Any, Dict, Optional


class LinkedInAction:
    """
    Manages approved LinkedIn outreach.
    STRICT RULE: Only executes or provides action links when explicitly approved by the user.
    Never sends background automated messages without approval.
    """

    @classmethod
    def generate_action_payload(
        cls,
        linkedin_url: str,
        message: str,
        recipient_name: str,
        action_type: str = "connection_request",
    ) -> Dict[str, Any]:
        """
        Generates deep-links and approved action package for one-tap execution.
        """
        clean_url = (linkedin_url or "").strip()
        encoded_msg = urllib.parse.quote(message)

        # Build direct web URL
        profile_url = clean_url if clean_url.startswith("http") else f"https://www.linkedin.com/in/{clean_url}"

        # LinkedIn Web direct messaging URL format if available
        direct_message_url = f"https://www.linkedin.com/messaging/thread/new/?recipient={clean_url}"

        return {
            "recipient_name": recipient_name,
            "profile_url": profile_url,
            "direct_message_url": direct_message_url,
            "message_text": message,
            "character_count": len(message),
            "is_within_connection_limit": len(message) <= 300,
            "approval_required": True,
            "recommended_action": "Approve & Open LinkedIn",
        }
