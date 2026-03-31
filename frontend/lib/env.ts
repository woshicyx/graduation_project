import { z } from "zod";

/**
 * 前端所需环境变量（仅 NEXT_PUBLIC_* 在浏览器端可用）
 * 完整配置见项目根目录 .env.local
 */
const envSchema = z.object({
  NEXT_PUBLIC_API_URL: z
    .string()
    .url()
    .optional()
    .default("http://localhost:3000/api"),
});

export const env = envSchema.parse({
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
});

export type Env = z.infer<typeof envSchema>;
