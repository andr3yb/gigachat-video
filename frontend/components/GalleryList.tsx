"use client";

import { useEffect, useState } from "react";
import { deleteVideo, getVideos, type GenerationOut } from "@/lib/api";

function statusClass(status: string): string {
  switch (status) {
    case "DONE":
      return "done";
    case "FAILED":
      return "failed";
    case "PROCESSING":
      return "processing";
    default:
      return "pending";
  }
}

export default function GalleryList() {
  const [items, setItems] = useState<GenerationOut[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const load = async () => {
    try {
      const data = await getVideos();
      setItems(data);
      setError("");
    } catch {
      setError("Не удалось загрузить список видео");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const onDelete = async (id: number) => {
    try {
      setDeletingId(id);
      await deleteVideo(id);
      setItems((prev) => prev.filter((item) => item.id !== id));
    } catch {
      setError("Не удалось удалить видео");
    } finally {
      setDeletingId(null);
    }
  };

  if (isLoading) {
    return <p className="muted">Загрузка галереи...</p>;
  }

  if (error) {
    return <p className="error">{error}</p>;
  }

  if (items.length === 0) {
    return <p className="muted">Пока нет генераций</p>;
  }

  return (
    <div className="gallery-grid" style={{ marginTop: 16 }}>
      {items.map((item) => (
        <article key={item.id} className="card">
          <div className="row" style={{ justifyContent: "space-between" }}>
            <h3 style={{ margin: 0 }}>#{item.id}</h3>
            <span className={`status-pill ${statusClass(String(item.status))}`}>{item.status}</span>
          </div>
          <p style={{ marginTop: 10 }}>{item.prompt}</p>
          <p className="muted">Качество: {item.quality}</p>
          {item.video_url ? (
            <>
              <video className="video" src={item.video_url} controls playsInline />
              <div className="row" style={{ marginTop: 10 }}>
                <a className="btn secondary" href={item.video_url} target="_blank" rel="noreferrer">
                  Открыть
                </a>
                <a className="btn secondary" href={item.video_url} download>
                  Скачать
                </a>
              </div>
            </>
          ) : (
            <p className="muted">Видео ещё не готово</p>
          )}

          <button
            type="button"
            className="btn secondary"
            style={{ marginTop: 10 }}
            disabled={deletingId === item.id}
            onClick={() => void onDelete(item.id)}
          >
            {deletingId === item.id ? "Удаление..." : "Удалить"}
          </button>
        </article>
      ))}
    </div>
  );
}
