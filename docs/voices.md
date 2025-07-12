## Voices

- **Installation**:  
  Place all `.onnx` and `.onnx.json` files in the projects folder `models/voices`

- **Requirements**:  
  Each voice requires an `.onnx` model with its matching `.onnx.json` config.

- **Quality**:  
  Prefer `high` models for best naturalness and clarity; `medium` is a strong fallback if `high` is unavailable.

## Available Voices

| Alias       | Filename                  | Speaker ID | Quality | Gender | Description                                                        |
|-------------|---------------------------|------------|---------|--------|--------------------------------------------------------------------|
| `amy`       | `en_US-amy-medium`        | -          | Medium  | Female | Soft, friendly, and natural—ideal for casual conversations         |
| `sandy`     | `en_US-hfc_female-medium` | -          | Medium  | Female | Clear and modern with a slightly upbeat tone                       |
| `tom`       | `en_US-hfc_male-medium`   | -          | Medium  | Male   | Calm and balanced male voice with smooth delivery                  |
| `wendy`     | `en_US-ljspeech-high`     | -          | High    | Female | Articulate and expressive, great for narration and clarity         |
| `emma`      | `en_US-libritts_r-medium` | 18         | Medium  | Female | Friendly, energetic, and clear                                     |
| `olivia`    | `en_US-libritts_r-medium` | 15         | Medium  | Female | Warm and expressive with a conversational tone                     |
| `mark`      | `en_US-libritts_r-medium` | 3          | Medium  | Male   | Deep and assertive with a touch of grit                            |
| `john`      | `en_US-libritts_r-medium` | 19         | Medium  | Male   | Confident and steady with a warm, engaging tone                    |
| `cori`      | `en_GB-cori-high`         | -          | High    | Female | Polished British accent, formal and professional tone              |
| `prudence`  | `en_GB-semaine-medium`    | 0          | Medium  | Female | Crisp and formal British voice with clarity                        |
| `poppy`     | `en_GB-semaine-medium`    | 4          | Medium  | Female | Youthful and light British accent, gentle and friendly             |

 

---

## Additional

- Only `.onnx` and `.onnx.json` files are required for synthesis—other files and folders can be safely deleted to save space.
- For more voices or updates, visit the official **Piper voices repository** on [Hugging Face](https://huggingface.co/piper-tts).
