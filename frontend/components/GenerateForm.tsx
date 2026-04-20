"use client";

import { FormEvent, useMemo, useRef, useState } from "react";
import { createGeneration, type GenerationOut, type Quality } from "@/lib/api";
import TaskStatusPoller from "@/components/TaskStatusPoller";

const ACCEPTED_TYPES = "image/png,image/jpeg,image/webp";

export default function GenerateForm() {
  const [prompt, setPrompt] = useState("");
  const [quality, setQuality] = useState<Quality>("480P");
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [generation, setGeneration] = useState<GenerationOut | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const fileLabel = useMemo(() => {
    if (!file) {
      return "Перетащите изображение сюда или выберите файл";
    }
    return `Выбран файл: ${file.name}`;
  }, [file]);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
      setError("Добавьте изображение для генерации");
      return;
    }

    setIsSubmitting(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("prompt", prompt);
      formData.append("quality", quality);
      formData.append("file", file);

      const created = await createGeneration(formData);
      setGeneration(created);
    } catch (e) {
      const message = e instanceof Error ? e.message : "Не удалось отправить задачу";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <form className="card" onSubmit={onSubmit}>
        <h2>Генерация видео</h2>

        <label htmlFor="prompt">Промпт</label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          minLength={1}
          maxLength={2000}
          required
          rows={5}
          style={{ width: "100%", marginTop: 8 }}
          placeholder="Опишите желаемую анимацию"
        />

        <div style={{ marginTop: 16 }}>
          <span>Качество:</span>
          <div className="row" style={{ marginTop: 8 }}>
            <label>
              <input
                type="radio"
                name="quality"
                value="480P"
                checked={quality === "480P"}
                onChange={() => setQuality("480P")}
              />{" "}
              480P
            </label>
            <label>
              <input
                type="radio"
                name="quality"
                value="720P"
                checked={quality === "720P"}
                onChange={() => setQuality("720P")}
              />{" "}
              720P
            </label>
          </div>
        </div>

        <div
          className={`dropzone ${isDragging ? "active" : ""}`}
          style={{ marginTop: 16 }}
          onDragEnter={(event) => {
            event.preventDefault();
            setIsDragging(true);
          }}
          onDragOver={(event) => {
            event.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={(event) => {
            event.preventDefault();
            setIsDragging(false);
          }}
          onDrop={(event) => {
            event.preventDefault();
            setIsDragging(false);
            const droppedFile = event.dataTransfer.files?.[0];
            if (droppedFile) {
              setFile(droppedFile);
            }
          }}
          onClick={() => inputRef.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") {
              inputRef.current?.click();
            }
          }}
        >
          <p>{fileLabel}</p>
          <p className="muted">Форматы: JPG, PNG, WEBP (до 20 МБ)</p>
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPTED_TYPES}
            onChange={(event) => {
              const selectedFile = event.target.files?.[0] ?? null;
              setFile(selectedFile);
            }}
            hidden
          />
        </div>

        {error && (
          <p style={{ color: "tomato", marginTop: 16 }} role="alert">
            {error}
          </p>
        )}

        <button type="submit" disabled={isSubmitting} style={{ marginTop: 16 }}>
          {isSubmitting ? "Отправка..." : "Сгенерировать"}
        </button>
      </form>

      {generation && <TaskStatusPoller generationId={generation.id} />}
    </>
  );
}
