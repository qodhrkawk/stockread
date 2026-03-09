import { z } from "zod";

const CardSchema = z.object({
  name: z.string(),
  price: z.string().optional(),
  change: z.string().optional(),
  indicators: z.array(z.string()).optional(),
  reason: z.string().optional(),
});

const SceneSchema = z.object({
  label: z.enum(["hook", "summary", "detail", "context", "closing"]),
  tts_text: z.string(),
  cards: z.array(CardSchema).optional(),
  // hook용
  headline: z.string().optional(),
  number: z.string().optional(),
  // summary용
  sectors: z.array(z.object({
    name: z.string(),
    direction: z.enum(["up", "down"]),
  })).optional(),
  // context용
  flow: z.array(z.string()).optional(),
  // closing용
  message: z.string().optional(),
  duration: z.number(),
});

export const ShortVideoSchema = z.object({
  date: z.string(),
  title: z.string(),
  tts_script: z.string(),
  scenes: z.array(SceneSchema),
  audioDurationSec: z.number().optional(),
});

export type Card = z.infer<typeof CardSchema>;
export type Scene = z.infer<typeof SceneSchema>;
export type ShortScript = z.infer<typeof ShortVideoSchema>;
