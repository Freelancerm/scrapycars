import random


class RotateUserAgentMiddleware:

    def process_request(self, request, spider):
        user_agents = spider.settings.get('USER_AGENTS')
        if user_agents:
            user_agent = random.choice(user_agents)
            request.headers["User-Agent"] = user_agent
            spider.logger.debug(f"Using Random User-Agent: {user_agent}")