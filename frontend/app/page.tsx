import GenerateForm from "@/components/GenerateForm";

export default function HomePage() {
  return (
    <>
      <h1>AI Video Factory</h1>
      <p className="muted">Загрузите изображение, задайте промпт и дождитесь генерации.</p>
      <GenerateForm />
    </>
  );
}
