import React, { useEffect, useState } from "react";
import EmailList from "./components/EmailList";
import UploadEmail from "./components/UploadEmail";
import Login from "./components/Login";

function App() {
  const [user, setUser] = useState(null);
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchMe = async () => {
    try {
      const res = await fetch("/api/auth/me", { credentials: "include" });
      if (!res.ok) {
        setUser(null);
        return;
      }
      setUser(await res.json());
    } catch {
      setUser(null);
    }
  };

  const fetchEmails = async () => {
    try {
      const res = await fetch("/api/emails", { credentials: "include" });
      if (!res.ok) return;
      setEmails(await res.json());
    } catch (err) {
      console.error("Errore nel caricamento email:", err);
    }
  };

  const logout = async () => {
    await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
    setUser(null);
    setEmails([]);
  };

  useEffect(() => {
    (async () => {
      await fetchMe();
      setLoading(false);
    })();
  }, []);

  useEffect(() => {
    if (user) fetchEmails();
  }, [user]);

  if (loading) return <p style={{ padding: "2rem" }}>Caricamento...</p>;
  if (!user) return <Login />;

  return (
    <div style={{ fontFamily: "sans-serif", padding: "2rem" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>GMN Mail Interface</h1>
        <div>
          <span style={{ marginRight: "1rem" }}>{user.email}</span>
          <button onClick={logout}>Esci</button>
        </div>
      </header>
      <UploadEmail onUploaded={fetchEmails} />
      <EmailList emails={emails} />
    </div>
  );
}

export default App;
