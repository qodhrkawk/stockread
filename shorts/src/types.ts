import { z } from "zod";

const CardSchema = z.object({
  name: z.string(),
  price: z.string().optional(),
  change: z.string().optional(),
  reason: z.string().optional(),
  indicators: z.array(z.string()).optional(),
});

const VisualSegmentSchema = z.object({
  start_sentence: z.number(),
  card: CardSchema.optional(),
  sector: z.object({
    name: z.string(),
    direction: z.enum(["up", "down"]),
    change: z.string().optional(),
  }).optional(),
  flow_item: z.string().optional(),
});

const SceneSchema = z.object({
  label: z.enum(["hook", "summary", "detail", "context", "closing"]),
  tts_text: z.string(),
  visual_segments: z.array(VisualSegmentSchema).optional(),
  // hook
  event: z.string().optional(),
  number: z.string().optional(),
  // context
  flow: z.array(z.string()).optional(),
  // closing
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
export type VisualSegment = z.infer<typeof VisualSegmentSchema>;
export type Scene = z.infer<typeof SceneSchema>;
export type ShortScript = z.infer<typeof ShortVideoSchema>;
