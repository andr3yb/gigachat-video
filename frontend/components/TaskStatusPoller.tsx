"use client";

import { useEffect, useState } from "react";
import { getTaskStatus, type TaskStatus } from "@/lib/api";

type Props = {
  generationId: number;
};

const TERMINAL_STATUSES = new Set(["DONE", "FAILED"]);

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

  return (
    <div className="card">
      <h3>Статус генерации #{task.id}</h3>
      <p>Текущий статус: {task.status}</p>
      {task.error_message && <p>Ошибка: {task.error_message}</p>}
      {task.video_url && (
        <p>
          <a href={task.video_url} target="_blank" rel="noreferrer">
            Открыть видео
          </a>
        </p>
      )}
    </div>
  );
}
