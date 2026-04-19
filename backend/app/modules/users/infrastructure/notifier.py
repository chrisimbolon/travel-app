from abc import ABC, abstractmethod


class OtpNotifier(ABC):
    @abstractmethod
    async def send_otp(self, phone: str, code: str) -> None:
        pass


class ConsoleOtpNotifier(OtpNotifier):
    """DEV only — prints OTP to console instead of sending via WhatsApp."""
    async def send_otp(self, phone: str, code: str) -> None:
        print(f"[DEV] OTP for +{phone}: {code}")


class WhatsAppOtpNotifier(OtpNotifier):
    """
    PROD — calls WhatsApp Business API.
    Swap ConsoleOtpNotifier for this in production DI.
    """
    def __init__(self, api_url: str, api_token: str):
        self.api_url = api_url
        self.api_token = api_token

    async def send_otp(self, phone: str, code: str) -> None:
        import httpx
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.api_url}/messages",
                headers={"Authorization": f"Bearer {self.api_token}"},
                json={
                    "to": f"+{phone}",
                    "type": "template",
                    "template": {
                        "name": "otp_verification",
                        "components": [{
                            "type": "body",
                            "parameters": [{"type": "text", "text": code}],
                        }],
                    },
                },
                timeout=10,
            )