import { z } from "zod";

const SceneSchema = z.object({
  label: z.enum(["hook", "summary", "detail", "context", "closing"]),
  text: z.string(),
  tts_text: z.string().optional(),
  duration: z.number(),
});

export const ShortVideoSchema = z.object({
  date: z.string(),
  title: z.string(),
  tts_script: z.string(),
  scenes: z.array(SceneSchema),
  audioDurationSec: z.number().optional(),
});

export type Scene = z.infer<typeof SceneSchema>;
export type ShortScript = z.infer<typeof ShortVideoSchema>;
