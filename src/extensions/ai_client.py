import os
import torch
import logging
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from transformers.utils import logging as hf_logging
from huggingface_hub import login

logger = logging.getLogger(__name__)
hf_logging.set_verbosity_info()

class AIModel:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.pipe = None

    def load(self):
        login(os.getenv("HUGGINGFACE_TOKEN"))
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            load_in_8bit=True,
            device_map="auto",
            torch_dtype=torch.float16
        )
        self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

class BaseAI:
    def __init__(self, model_name="mistralai/Mistral-7B-Instruct-v0.1"):
        logger.info("Initializing BaseAI...")
        self.model = AIModel(model_name)
        self.model.load()

    def get_response(self, prompt, **kwargs):
        full_prompt = f"[INST] {prompt.strip()} [/INST]"
        logger.debug(f"Prompt sent to model: {full_prompt}")

        gen_kwargs = {
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": False,
            **kwargs
        }

        try:
            output = self.model.pipe(full_prompt, **gen_kwargs)
            response = output[0]["generated_text"].strip()
            logger.info("Model response: %s", response[:50] + "..." if len(response) > 50 else response)
            return response
        except Exception as e:
            logger.error(f"Model generation failed: {e}", exc_info=True)
            raise RuntimeError(f"Model error: {e}")

class ListenerAI:
    def __init__(self, base: BaseAI):
        self.base = base

    def detect_activation(self, messages: list[str]) -> bool:
        if not isinstance(messages, list):
            raise TypeError("Expected a list of strings for `messages`.")
    
        prompt = (
            "Does the following conversation include someone speaking to the AI named Ava?\n\n"
            "Return only 'True' or 'False'.\n"
            f"{''.join(messages)}\n\n"
            "Answer:"
        )
        response = self.base.get_response(
            prompt,
            max_new_tokens=5,
            do_sample=False
        ).lower()
        
        return "true" in response.lower().strip()


class IntentClassifierAI:
    def __init__(self, base: BaseAI):
        self.base = base

    def classify_intent(self, messages: list[str]) -> str:
        prompt = (
            "Determine whether the following message is a command or part of a conversation directed at Ava. "
            "Respond only with 'command' or 'conversation'.\n\n"
            + "\n".join(messages) +
            "\n\nIntent:"
        )
        response = self.base.get_response(
            prompt,
            max_new_tokens=5,
            do_sample=False
        ).lower()
        
        return response.lower().strip()
    
class CommandExtractorAI:
    def __init__(self, base: BaseAI):
        self.base = base

    def extract_command(self, messages: list[str]) -> str:
        prompt = (
            "Extract the command directed at Ava from this conversation. "
            "Return only the command as a sentence or phrase.\n\n" + "\n".join(messages)
        )
        return self.base.get_response(prompt)


class ResponderAI:
    def __init__(self, base: BaseAI):
        self.base = base

    def generate_reply(self, command: str) -> str:
        prompt = (
            f"The AI named Ava (You) received this command: '{command}'. "
            "Respond with a helpful and natural-sounding reply."
        )
        
        response = self.base.get_response(
            prompt
        )
        
        return response


class AIClient:
    def __init__(self):
        logger.info("Initializing AI Client...")
        self.base_ai = BaseAI()

        self.listener = ListenerAI(self.base_ai)
        self.intent_classifier = IntentClassifierAI(self.base_ai)
        self.command_extractor = CommandExtractorAI(self.base_ai)
        self.responder = ResponderAI(self.base_ai)

    def handle_user_input(self, user_message: str) -> str:
        logger.debug(f"AIClient received input: {user_message!r}")
        if not user_message.strip():
            return "No input detected."

        message = [user_message]

        if self.listener.detect_activation(message):
            intent = self.intent_classifier.classify_intent(message)
            if intent == "command":
                # logger.info("Command detected.")
                # command = self.command_extractor.extract_command(message)
                # if command:
                #     logger.info(f"Command extracted: {command}")
                #     return self.responder.generate_reply(command)
                return
            elif intent == "conversation":
                response = self.responder.generate_reply(user_message)
                return response
        else:
            logger.info("No command detected.")
            return
