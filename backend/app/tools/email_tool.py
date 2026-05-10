import logging
from datetime import datetime

logger = logging.getLogger("nexusai.email")


async def send_email(to: str, subject: str, body: str) -> str:
    """Simulate sending an email — logs to console, returns confirmation."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_output = (
        f"\n{'='*50}\n"
        f"📧  SIMULATED EMAIL\n"
        f"{'='*50}\n"
        f"To:      {to}\n"
        f"Subject: {subject}\n"
        f"Date:    {timestamp}\n"
        f"{'─'*50}\n"
        f"{body}\n"
        f"{'='*50}"
    )
    logger.info(log_output)
    print(log_output)

    return (
        f"✅ Email sent successfully!\n\n"
        f"**To:** {to}  \n"
        f"**Subject:** {subject}  \n"
        f"**Sent at:** {timestamp}"
    )
