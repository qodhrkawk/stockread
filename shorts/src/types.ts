import { z } from "zod";

export const ShortVideoSchema = z.object({
  date: z.string(),
  title: z.string(),
  market_summary: z.string(),
  highlights: z.array(z.string()),
  interpretation: z.string(),
  tts_script: z.string(),
  audioDurationSec: z.number().optional(),
});

export type ShortScript = z.infer<typeof ShortVideoSchema>;
