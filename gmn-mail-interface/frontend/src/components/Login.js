import React, { useState } from "react";

function Login() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setStatus(null);
    try {
      const res = await fetch("/api/auth/request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      if (!res.ok) throw new Error("Errore richiesta");
      setStatus("sent");
    } catch (err) {
      setStatus("error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: 360, margin: "4rem auto", fontFamily: "sans-serif" }}>
      <h2>Accedi a GMN Mail Interface</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          required
          placeholder="tu@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ width: "100%", padding: "0.6rem", marginBottom: "0.6rem" }}
        />
        <button type="submit" disabled={submitting} style={{ padding: "0.6rem 1rem" }}>
          {submitting ? "Invio..." : "Inviami il magic link"}
        </button>
      </form>

      {status === "sent" && (
        <p style={{ color: "green" }}>
          Se l'indirizzo è autorizzato riceverai un'email con il link di accesso.
        </p>
      )}
      {status === "error" && (
        <p style={{ color: "crimson" }}>Errore. Riprova tra qualche secondo.</p>
      )}

      <hr style={{ margin: "1.5rem 0" }} />
      <a href="/api/auth/google/login">Accedi con Google</a>
    </div>
  );
}

export default Login;
