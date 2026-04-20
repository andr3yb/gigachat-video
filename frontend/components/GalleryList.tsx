"use client";

import { useEffect, useState } from "react";
import { deleteVideo, getVideos, type GenerationOut } from "@/lib/api";

export default function GalleryList() {
  const [items, setItems] = useState<GenerationOut[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

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
      await deleteVideo(id);
      setItems((prev) => prev.filter((item) => item.id !== id));
    } catch {
      setError("Не удалось удалить видео");
    }
  };

  if (isLoading) {
    return <p className="muted">Загрузка галереи...</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }

  if (items.length === 0) {
    return <p className="muted">Пока нет генераций</p>;
  }

  return (
    <div className="gallery-grid" style={{ marginTop: 16 }}>
      {items.map((item) => (
        <article key={item.id} className="card">
          <h3>#{item.id}</h3>
          <p className="muted">Статус: {item.status}</p>
          <p>{item.prompt}</p>
          <p className="muted">Качество: {item.quality}</p>
          {item.video_url ? (
            <div className="row">
              <a href={item.video_url} target="_blank" rel="noreferrer">
                Открыть
              </a>
              <a href={item.video_url} download>
                Скачать
              </a>
            </div>
          ) : (
            <p className="muted">Видео ещё не готово</p>
          )}

          <button type="button" style={{ marginTop: 10 }} onClick={() => void onDelete(item.id)}>
            Удалить
          </button>
        </article>
      ))}
    </div>
  );
}
