import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const form = new FormData();
    form.append("file", file);
    const res = await fetch("/api/extract", {
      method: "POST",
      body: form
    });
    if (!res.ok) {
      const err = await res.json();
      alert(err.detail || "Erro desconhecido");
      setLoading(false);
      return;
    }
    const data = await res.json();
    setText(data.text);
    setLoading(false);
  };

  return (
    <main style={{ padding: 24, maxWidth: 800, margin: "0 auto" }}>
      <h1>Extrator de Texto de PDFs</h1>
      <p>Envie um PDF e receba o texto extraído pelo docTR.</p>

      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => {
          setFile(e.target.files[0]);
          setText("");
        }}
      />
      <button
        onClick={handleUpload}
        disabled={!file || loading}
        style={{ marginLeft: 8 }}
      >
        {loading ? "Processando..." : "Extrair Texto"}
      </button>

      {text && (
        <>
          <h2>Texto extraído</h2>
          <textarea
            readOnly
            value={text}
            rows={20}
            style={{ width: "100%", fontFamily: "monospace" }}
          />
        </>
      )}
    </main>
  );
}
