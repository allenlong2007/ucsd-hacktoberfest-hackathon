// Readable names for audit_result.model / approaches[].model. Unknown ids are shown as-is.
const MODEL_NAMES: Record<string, string> = {
  'gemini:models/gemma-4-26b-a4b-it': 'Gemma 4 26B via Gemini API',
  'ollama:gemma4:e2b': 'Gemma 4 E2B local (Ollama)',
}

export function modelName(model: string): string {
  return MODEL_NAMES[model] ?? model
}
