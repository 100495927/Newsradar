const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function App() {
  return (
    <main style={{ fontFamily: "system-ui, sans-serif", padding: "2rem" }}>
      <h1>NewsRadar Frontend</h1>
      <p>Base API configurada: {apiBaseUrl}</p>
      <p>Estructura React preparada para desarrollo.</p>
    </main>
  );
}
