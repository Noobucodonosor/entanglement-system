import React, { useEffect, useState } from "react";
import EmailList from "./components/EmailList";
import UploadEmail from "./components/UploadEmail";

function App() {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchEmails = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/emails");
      const data = await res.json();
      setEmails(data);
    } catch (err) {
      console.error("Errore nel caricamento email:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmails();
  }, []);

  return (
    <div style={{ fontFamily: "sans-serif", padding: "2rem" }}>
      <h1>GMN Mail Interface</h1>
      <UploadEmail onUploaded={fetchEmails} />
      {loading ? <p>Caricamento...</p> : <EmailList emails={emails} />}
    </div>
  );
}

export default App;
