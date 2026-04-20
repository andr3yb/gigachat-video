import GalleryList from "@/components/GalleryList";

export default function GalleryPage() {
  return (
    <>
      <h1 className="hero-title">Галерея</h1>
      <p className="muted">Все генерации в одном месте: предпросмотр, скачивание и удаление.</p>
      <GalleryList />
    </>
  );
}
