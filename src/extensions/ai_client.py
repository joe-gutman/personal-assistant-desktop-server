import openai

class AIClient:
    def __init__(self):
        self.api_key = None

    def init_app(self, app):
        self.api_key = app.config.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set in the configuration.")
        openai.api_key = self.api_key  # Optional: can also pass in each call

    def get_response(self, prompt, **kwargs):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                api_key=self.api_key,  # safer than setting global
                **kwargs
            )
            return response.choices[0].message['content']
        except Exception as e:
            raise RuntimeError(f"Error calling OpenAI API: {e}")
