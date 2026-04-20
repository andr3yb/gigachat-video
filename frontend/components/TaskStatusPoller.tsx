"use client";

import { useEffect, useState } from "react";
import { getTaskStatus, type TaskStatus } from "@/lib/api";

type Props = {
  generationId: number;
};

const TERMINAL_STATUSES = new Set(["DONE", "FAILED"]);
const STATUS_PROGRESS: Record<string, number> = {
  PENDING: 20,
  PROCESSING: 70,
  DONE: 100,
  FAILED: 100
};

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

export default function TaskStatusPoller({ generationId }: Props) {
  const [task, setTask] = useState<TaskStatus | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    let isMounted = true;
    let timer: NodeJS.Timeout | undefined;

    const poll = async () => {
      try {
        const nextTask = await getTaskStatus(generationId);
        if (!isMounted) {
          return;
        }
        setTask(nextTask);
        setError("");

        if (!TERMINAL_STATUSES.has(nextTask.status)) {
          timer = setTimeout(poll, 3000);
        }
      } catch {
        if (!isMounted) {
          return;
        }
        setError("Не удалось получить статус задачи");
        timer = setTimeout(poll, 3000);
      }
    };

    void poll();

    return () => {
      isMounted = false;
      if (timer) {
        clearTimeout(timer);
      }
    };
  }, [generationId]);

  if (error) {
    return <p className="muted">{error}</p>;
  }

  if (!task) {
    return <p className="muted">Загрузка статуса...</p>;
  }

  const status = String(task.status || "PENDING").toUpperCase();
  const progress = STATUS_PROGRESS[status] ?? 20;

  return (
    <div className="card">
      <div className="row" style={{ justifyContent: "space-between" }}>
        <h3 style={{ margin: 0 }}>Статус генерации #{task.id}</h3>
        <span className={`status-pill ${statusClass(status)}`}>{status}</span>
      </div>
      <div className="progress" style={{ marginTop: 10 }}>
        <span style={{ width: `${progress}%` }} />
      </div>
      <p className="muted" style={{ marginBottom: 0 }}>
        Прогресс: {progress}%
      </p>

      {task.error_message && <p className="error">Ошибка: {task.error_message}</p>}
      {task.video_url && (
        <>
          <video className="video" src={task.video_url} controls playsInline />
          <div className="row" style={{ marginTop: 10 }}>
            <a className="btn secondary" href={task.video_url} target="_blank" rel="noreferrer">
              Открыть в новой вкладке
            </a>
            <a className="btn secondary" href={task.video_url} download>
              Скачать MP4
            </a>
          </div>
        </>
      )}
    </div>
  );
}
