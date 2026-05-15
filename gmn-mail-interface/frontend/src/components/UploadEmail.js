import React, { useState } from "react";

function UploadEmail({ onUploaded }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    const data = new FormData();
    data.append("file", file);
    try {
      await fetch("/api/emails/upload", { method: "POST", body: data });
      setFile(null);
      onUploaded?.();
    } catch (err) {
      console.error("Errore upload:", err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: "1rem" }}>
      <input
        type="file"
        accept=".eml"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />
      <button type="submit" disabled={!file || uploading}>
        {uploading ? "Carico..." : "Carica email"}
      </button>
    </form>
  );
}

export default UploadEmail;
