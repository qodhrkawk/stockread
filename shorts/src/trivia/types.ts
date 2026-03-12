import { z } from "zod";

const StepSchema = z.object({
  icon: z.string(),
  text: z.string(),
});

const TriviaSceneSchema = z.object({
  label: z.enum(["hook", "explain", "twist", "closing"]),
  tts_text: z.string(),
  duration: z.number(),
  // hook
  question: z.string().optional(),
  fact: z.string().optional(),
  // explain
  steps: z.array(StepSchema).optional(),
  // twist
  highlight: z.string().optional(),
  detail: z.string().optional(),
  // closing
  message: z.string().optional(),
  // 공통
  image_prompt: z.string().optional(),
});

export const TriviaScriptSchema = z.object({
  date: z.string(),
  title: z.string(),
  tts_script: z.string(),
  scenes: z.array(TriviaSceneSchema),
  topic_id: z.string().optional(),
  category: z.string().optional(),
  emoji: z.string().optional(),
  audioDurationSec: z.number().optional(),
});

export type Step = z.infer<typeof StepSchema>;
export type TriviaScene = z.infer<typeof TriviaSceneSchema>;
export type TriviaScript = z.infer<typeof TriviaScriptSchema>;
