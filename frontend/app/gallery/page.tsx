import GalleryList from "@/components/GalleryList";

export default function GalleryPage() {
  return (
    <>
      <h1>Галерея</h1>
      <p className="muted">Список всех генераций, скачивание и удаление.</p>
      <GalleryList />
    </>
  );
}
