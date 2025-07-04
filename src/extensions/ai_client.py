from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

class AIClient:
    def __init__(self, model_name="mistralai/Mistral-7B-Instruct-v0.1"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.pipe = None

    def init_app(self, app=None):
        print(f"Loading model '{self.model_name}' with 8-bit quantization...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            load_in_8bit=True,
            device_map="auto",
            torch_dtype=torch.float16
        )
        self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer, device=0)

    def get_response(self, prompt, **kwargs):
        full_prompt = self._format_prompt(prompt)
        try:
            output = self.pipe(
                full_prompt,
                max_new_tokens=512,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                return_full_text=False
            )
            return output[0]["generated_text"].strip()
        except Exception as e:
            raise RuntimeError(f"Local model error: {e}")

    def _format_prompt(self, user_message):
        return f"[INST] {user_message.strip()} [/INST]"