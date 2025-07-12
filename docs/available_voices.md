## 🔊 Available Voices

| Alias               | Filename                  | Quality | Gender | Description                                         |
|---------------------|---------------------------|---------|--------|-----------------------------------------------------|
| `amy-medium`        | `en_US-amy-medium`        | Medium  | Female | Soft, natural, friendly tone                        |
| `hfc-female-medium` | `en_US-hfc_female-medium` | Medium  | Female | Modern, pleasant, clear articulation                |
| `lessac-high`       | `en_US-lessac-high`       | High    | Female | Expressive, rich tone, community favorite           |
| `ljspeech-high`     | `en_US-ljspeech-high`     | High    | Female | Based on LJ Speech dataset, articulate and clear    |
| `hfc-male-medium`   | `en_US-hfc_male-medium`   | Medium  | Male   | Balanced, smooth, modern male voice                 |

## 🛠️ Usage & Best Practices

- **Default Directory**:  
  Place all `.onnx` and `.onnx.json` files in:  
  `~/.local/share/piper-tts/piper-voices/` (Linux/WSL)

- **Pairing**:  
  Always keep each `.onnx` model with its matching `.onnx.json` config.

- **Quality**:  
  Prefer `high` models for best naturalness and clarity; `medium` is a strong fallback if `high` is unavailable.

---

## 📝 Additional Notes

- Only `.onnx` and `.onnx.json` files are required for synthesis—other files can be safely deleted to save space.

- For more voices or updates, visit the official **Piper voices repository** on [Hugging Face](https://huggingface.co/piper-tts).
