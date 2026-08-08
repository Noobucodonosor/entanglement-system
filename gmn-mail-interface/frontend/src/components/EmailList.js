import React from "react";

function EmailList({ emails }) {
  if (!emails.length) {
    return <p>Nessuna email caricata.</p>;
  }

  return (
    <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem" }}>
      <thead>
        <tr style={{ background: "#eee" }}>
          <th style={th}>Mittente</th>
          <th style={th}>Oggetto</th>
          <th style={th}>Punteggio</th>
          <th style={th}>Acconto (€)</th>
          <th style={th}>Ricevuta</th>
        </tr>
      </thead>
      <tbody>
        {emails.map((e) => (
          <tr key={e.id}>
            <td style={td}>{e.sender}</td>
            <td style={td}>{e.subject}</td>
            <td style={td}>{e.score}</td>
            <td style={td}>{e.deposit.toFixed(2)}</td>
            <td style={td}>{e.received_at || "-"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

const th = { textAlign: "left", padding: "0.5rem", borderBottom: "1px solid #ccc" };
const td = { padding: "0.5rem", borderBottom: "1px solid #eee" };

export default EmailList;
