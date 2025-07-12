import os
import torch
import logging
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, GenerationConfig
from transformers.utils import logging as hf_logging

logger = logging.getLogger(__name__)

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
                return "Command detected, but no action was taken."
            elif intent == "conversation":
                response = self.responder.generate_reply(user_message)
                return response
        else:
            logger.info("No command detected.")
            return None  # Explicitly return None when no activation detected
        
class AIModel:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.pipe = None

    def load(self):
        logger.info(f"Loading model from local path: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            local_files_only=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            local_files_only=True,
            load_in_8bit=True,
            device_map="auto",
            torch_dtype=torch.float16,
        )
        self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

class BaseAI:
    def __init__(self, model_name="models/llm/Mistral-7B-Instruct-v0.1"):
        self.model_name = os.path.abspath(model_name)
        logger.info("Initializing BaseAI...")
        self.model = AIModel(model_name)
        self.model.load()

    def get_response(self, prompt, **kwargs):
        full_prompt = f"[INST] {prompt.strip()} [/INST]"
        logger.debug(f"Prompt sent to model: {full_prompt}")

        do_sample = kwargs.get("do_sample", False)

        if not do_sample:
            for key in ["temperature", "top_p", "top_k"]:
                kwargs.pop(key, None)

        try:
            output = self.model.pipe(
                full_prompt,
                return_full_text=False,
                **kwargs
            )
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
            "Respond only with 'command' or 'conversation' or 'none'.\n\n"
            + "\n".join(messages) +
            "\n\nIntent:"
        )
        
        response = self.base.get_response(
            prompt,
            max_new_tokens=10,
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
    
        response = self.base.get_response(
            prompt,
            max_new_tokens=50,
            do_sample=False,
        ).strip()
        
        return response


class ResponderAI:
    def __init__(self, base: BaseAI):
        self.base = base

    def generate_reply(self, command: str) -> str:
        prompt = (
            f"The AI named Ava (You) received this command: '{command}'. "
            "Respond with a helpful and natural-sounding reply."
        )
        
        response = self.base.get_response(
            prompt,
            max_new_tokens=100,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            repetition_penalty=1.2,
        ).strip()
        
        return response


