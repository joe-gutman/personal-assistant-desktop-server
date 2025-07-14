import os
import yaml
import torch
import logging
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, GenerationConfig
from transformers.utils import logging as hf_logging

logger = logging.getLogger(__name__)

class AI:
    def __init__(self):
        self.config = None
        self.model = None
        self.model_name = None
        self.name = None
        self.prompts = None
        self._load_config()
        
    def _load_config(self):
        config_path = os.path.join("config", "ai.yaml")
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        if not config:
            raise ValueError(f"Configuration file at {config_path} is empty or invalid.")

        if config != self.config:
            self.config = config

            # Validate before applying
            if not all(k in self.config for k in ("name", "prompts", "model")):
                raise ValueError("Config mis sing required keys: 'name', 'prompts', or 'model'.")

            self.name = self.config["name"]
            self.prompts = self.config["prompts"]

            model_name = self.config["model"]["name"]
            if model_name != self.model_name:
                self.model_name = model_name
                self._load_model()

            logger.info("AI config updated.")

    def _load_model(self):
        model_path = os.path.join("models", "ai", self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            local_files_only=True,
            load_in_8bit=True,
            device_map="auto",
            torch_dtype=torch.float16,
        )
        self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

    def _generate(self, prompt, **kwargs):
        full_prompt = f"[INST] {prompt.strip()} [/INST]"
        if not kwargs.get("do_sample", False):
            for key in ["temperature", "top_p", "top_k"]:
                kwargs.pop(key, None)
        try:
            output = self.pipe(full_prompt, return_full_text=False, **kwargs)
            return output[0]["generated_text"].strip()
        except Exception as e:
            logger.error(f"Model generation failed: {e}", exc_info=True)
            raise RuntimeError(f"Model error: {e}")

    def detect_activation(self, message: str) -> bool:
        prompt = self.prompts["activation"].format(name=self.name, conversation=message)
        response = self._generate(prompt, max_new_tokens=5, do_sample=False).lower()
        return "true" in response

    def classify_intent(self, message: str) -> str:
        prompt = self.prompts["intent"].format(name=self.name, conversation=message)
        return self._generate(prompt, max_new_tokens=10, do_sample=False).strip().lower()

    def extract_command(self, message: str) -> str:
        prompt = self.prompts["command_"].format(name=self.name, conversation=message)
        return self._generate(prompt, max_new_tokens=50, do_sample=False).strip()

    def generate_reply(self, command: str) -> str:
        prompt = self.prompts["response"].format(name=self.name, command=command)
        return self._generate(prompt, max_new_tokens=100, do_sample=True,
                              temperature=0.7, top_p=0.9, top_k=50, repetition_penalty=1.2).strip()

    def user_input(self, message: str) -> str | None:
        self._load_config()        
        if not message.strip():
            return "No input detected."
        if self.detect_activation(message):
            intent = self.classify_intent(message)
            if intent == "command":
                command = self.extract_command(message)
                return self.generate_reply(command)
            elif intent == "conversation":
                return self.generate_reply(message)
        return None
