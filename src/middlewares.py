import random


class RotateUserAgentMiddleware:

    USER_AGENTS = [
        "Chrome/135.0 (Windows NT 10.0; Win64; x64)...",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
        "Mozilla/6.0 (X11; Linux x86_64)...",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)...",
        "Mozilla/5.0 (Windows NT 10.0; WOW64)..."
    ]

    def process_request(self, request, spider):
        user_agent = random.choice(self.USER_AGENTS)

        request.headers["User-Agent"] = user_agent

        spider.logger.debug(f"Using User-Agent: {user_agent}")