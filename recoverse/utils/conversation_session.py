from camel.agents import ChatAgent
from camel.messages import BaseMessage
import sys

class ConversationSession:
    def __init__(self, agent: ChatAgent, user_name="User", assistant_name="Assistant"):
        self.agent = agent
        self.user_name = user_name
        self.assistant_name = assistant_name
        self.history = []

    def start(self):
        first_input = input(f"🧑 {self.user_name}: ")
        self.history.append(f"{self.user_name}: {first_input}")

        response = self.agent.step(first_input)
        assistant_reply = response.msgs[0].content
        print(f"🤖 {self.assistant_name}:", assistant_reply)
        self.history.append(f"{self.assistant_name}: {assistant_reply}")

        while True:
            user_input = input(f"🧑 {self.user_name}: ")
            if user_input.lower().strip() in ["done", "好了", "no more", "that's all"]:
                self.history.append(f"{self.user_name}: {user_input}")
                break

            self.history.append(f"{self.user_name}: {user_input}")

            assistant_reply = self.agent.step(user_input).msg.content
            print(f"🤖 {self.assistant_name}:", assistant_reply)
            self.history.append(f"{self.assistant_name}: {assistant_reply}")

    def get_full_conversation(self):
        return "\n".join(self.history)