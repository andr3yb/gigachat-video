import GenerateForm from "@/components/GenerateForm";

export default function HomePage() {
  return (
    <>
      <h1 className="hero-title">Генерация AI-видео</h1>
      <p className="muted">
        Загрузите изображение, задайте промпт и получите ролик прямо на странице с живым статусом.
      </p>
      <GenerateForm />
    </>
  );
}
