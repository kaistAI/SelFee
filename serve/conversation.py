import dataclasses
from enum import auto, Enum
from typing import List, Tuple, Any
# import logging

# logger = logging.getLogger("conversation")

PROMPT_DICT = {
    "prompt_input": (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Answer:\n"
    ),
    "prompt_no_input": (
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n### Answer:\n"
    ),
    "bare": (
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.\n\n"
    ),
}

class SeparatorStyle(Enum):
    """Different separator style."""
    SINGLE = auto()
    TWO = auto()


@dataclasses.dataclass
class Conversation:
    """A class that keeps all conversation history."""
    system: str
    roles: List[str]
    messages: List[List[str]]
    offset: int
    sep_style: SeparatorStyle = SeparatorStyle.SINGLE
    sep: str = "###"
    sep2: str = None

    skip_next: bool = False
    conv_id: Any = None

    def get_prompt(self):
        
        # Concat style
        ret = PROMPT_DICT["bare"]
        # ret = PROMPT_DICT["prompt_no_input"].format(instruction=self.messages[2][1])

        print("self.messages", self.messages)

        question_answers = []
        for role, message in self.messages[2:]:
            if not message:
                continue
            if "[DEBUG PURPOSE ONLY]" in message:
                continue

            is_revision = message.strip().startswith("Revision") and role == self.roles[1]
            is_feedback = message.strip().startswith("Feedback") and role == self.roles[0]
            is_answer = not is_revision and not is_feedback and role == self.roles[1]
            is_human = not is_revision and not is_feedback and role == self.roles[0]

            if is_human:
                question_answers.append({"human": message, "answers": []})
            if is_answer or is_revision:
                question_answers[-1]["answers"].append(message)

        print(f"question_answers | {question_answers}")

        trunc_answers = []
        for item in question_answers:
            trunc_answers.append((self.roles[0], item["human"]))
            if item["answers"]:
                last_answer = item["answers"][-1]
                last_answer = last_answer.strip()[len("Revision n:"):].strip()
                trunc_answers.append((self.roles[1], last_answer))

        print(f"trunc_answers | {trunc_answers}")
        for role, message in trunc_answers:
            if not message:
                continue
            if "[DEBUG PURPOSE ONLY]" in message:
                continue

            if role == self.roles[0]:
                ret = ret.strip() + "\n\n### Instruction:\n" + message + "\n\n### Answer:\n"
            elif role == self.roles[1]:
                ret = ret.strip() + "\n\n###" + message
        print("ret", ret)
        return ret

    def append_message(self, role, message):
        self.messages.append([role, message])

    def to_gradio_chatbot(self):
        ret = []
        for i, (role, msg) in enumerate(self.messages[self.offset:]):
            if role == self.roles[0]:
                ret.append([msg, None])
            elif role == self.roles[1]:
                ret.append([None, msg])
            else:
                raise ValueError(f"Invalid role: {role}")
        return ret

    def copy(self):
        return Conversation(
            system=self.system,
            roles=self.roles,
            messages=[[x, y] for x, y in self.messages],
            offset=self.offset,
            sep_style=self.sep_style,
            sep=self.sep,
            sep2=self.sep2,
            conv_id=self.conv_id)

    def dict(self):
        return {
            "system": self.system,
            "roles": self.roles,
            "messages": self.messages,
            "offset": self.offset,
            "sep": self.sep,
            "sep2": self.sep2,
            "conv_id": self.conv_id,
        }


conv_v1 = Conversation(
    system="A chat between a curious human and an artificial intelligence assistant. "
           "The assistant gives helpful, detailed, and polite answers to the human's questions.",
    roles=("Human", "Assistant"),
    messages=(
        ("Human", "Give three tips for staying healthy."),
        ("Assistant",
            "Sure, here are three tips for staying healthy:\n"
            "1. Exercise regularly: Regular physical activity can help improve your overall health and wellbeing. "
            "It can also help reduce your risk of chronic conditions such as obesity, diabetes, heart disease, "
            "and certain cancers. Aim for at least 150 minutes of moderate-intensity aerobic exercise or "
            "75 minutes of vigorous-intensity aerobic exercise per week, along with muscle-strengthening "
            "activities at least two days per week.\n"
            "2. Eat a balanced diet: Eating a balanced diet that is rich in fruits, "
            "vegetables, whole grains, lean proteins, and healthy fats can help support "
            "your overall health. Try to limit your intake of processed and high-sugar foods, "
            "and aim to drink plenty of water throughout the day.\n"
            "3. Get enough sleep: Getting enough quality sleep is essential for your physical "
            "and mental health. Adults should aim for seven to nine hours of sleep per night. "
            "Establish a regular sleep schedule and try to create a relaxing bedtime routine to "
            "help improve the quality of your sleep.")
    ),
    offset=2,
    sep_style=SeparatorStyle.SINGLE,
    sep="###",
)

conv_v1_2 = Conversation(
    system="A chat between a curious human and an artificial intelligence assistant. "
           "The assistant gives helpful, detailed, and polite answers to the human's questions.",
    roles=("Human", "Assistant"),
    messages=(
        ("Human", "What are the key differences between renewable and non-renewable energy sources?"),
        ("Assistant",
            "Renewable energy sources are those that can be replenished naturally in a relatively "
            "short amount of time, such as solar, wind, hydro, geothermal, and biomass. "
            "Non-renewable energy sources, on the other hand, are finite and will eventually be "
            "depleted, such as coal, oil, and natural gas. Here are some key differences between "
            "renewable and non-renewable energy sources:\n"
            "1. Availability: Renewable energy sources are virtually inexhaustible, while non-renewable "
            "energy sources are finite and will eventually run out.\n"
            "2. Environmental impact: Renewable energy sources have a much lower environmental impact "
            "than non-renewable sources, which can lead to air and water pollution, greenhouse gas emissions, "
            "and other negative effects.\n"
            "3. Cost: Renewable energy sources can be more expensive to initially set up, but they typically "
            "have lower operational costs than non-renewable sources.\n"
            "4. Reliability: Renewable energy sources are often more reliable and can be used in more remote "
            "locations than non-renewable sources.\n"
            "5. Flexibility: Renewable energy sources are often more flexible and can be adapted to different "
            "situations and needs, while non-renewable sources are more rigid and inflexible.\n"
            "6. Sustainability: Renewable energy sources are more sustainable over the long term, while "
            "non-renewable sources are not, and their depletion can lead to economic and social instability.\n")
    ),
    offset=2,
    sep_style=SeparatorStyle.SINGLE,
    sep="###",
)

conv_bair_v1 = Conversation(
    system="BEGINNING OF CONVERSATION:",
    roles=("USER", "GPT"),
    messages=(),
    offset=0,
    sep_style=SeparatorStyle.TWO,
    sep=" ",
    sep2="</s>",
)


default_conversation = conv_v1_2
conv_templates = {
    "v1": conv_v1_2,
    "bair_v1": conv_bair_v1,
}


if __name__ == "__main__":
    print(default_conversation.get_prompt())
