export type Quality = "480P" | "720P";
export type GenerationStatus = "PENDING" | "PROCESSING" | "DONE" | "FAILED";

export type GenerationOut = {
  id: number;
  status: GenerationStatus | string;
  prompt: string;
  quality: Quality | string;
  image_url: string;
  video_url: string | null;
  error_message: string | null;
  duration_sec: number | null;
  created_at: string;
  updated_at: string;
};

export type TaskStatus = {
  id: number;
  status: GenerationStatus | string;
  video_url: string | null;
  error_message: string | null;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost/api";

export async function createGeneration(formData: FormData): Promise<GenerationOut> {
  const response = await fetch(`${API_URL}/generate`, {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Failed to create generation");
  }

  return response.json();
}

export async function getTaskStatus(id: number): Promise<TaskStatus> {
  const response = await fetch(`${API_URL}/tasks/${id}`, {
    method: "GET",
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error("Failed to fetch task status");
  }
  return response.json();
}

export async function getVideos(): Promise<GenerationOut[]> {
  const response = await fetch(`${API_URL}/videos`, {
    method: "GET",
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error("Failed to fetch videos");
  }
  return response.json();
}

export async function deleteVideo(id: number): Promise<void> {
  const response = await fetch(`${API_URL}/videos/${id}`, { method: "DELETE" });
  if (!response.ok) {
    throw new Error("Failed to delete video");
  }
}
