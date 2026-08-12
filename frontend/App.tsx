import { FormEvent, useEffect, useRef, useState } from "react";

type Message = { role: "user" | "assistant"; content: string };

export default function App() {
  const [files, setFiles] = useState<string[]>([]);
  const [selected, setSelected] = useState("");
  const [content, setContent] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const session = useRef(crypto.randomUUID());

  const loadFile = async (path: string) => {
    const response = await fetch(`/api/files/${path}`);
    const data = await response.json() as { content: string };
    setSelected(path);
    setContent(data.content);
  };

  useEffect(() => {
    void fetch("/api/files").then((response) => response.json()).then((data: string[]) => {
      setFiles(data);
      if (data[0]) void loadFile(data[0]);
    });
  }, []);

  const send = async (event: FormEvent) => {
    event.preventDefault();
    const message = input.trim();
    if (!message || busy) return;
    setInput("");
    setBusy(true);
    setMessages((current) => [...current, { role: "user", content: message }]);
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: session.current, message }),
      });
      if (!response.ok) throw new Error();
      const data = await response.json() as { answer: string };
      setMessages((current) => [...current, {
        role: "assistant",
        content: data.answer,
      }]);
      const filesResponse = await fetch("/api/files");
      const nextFiles = await filesResponse.json() as string[];
      setFiles(nextFiles);
      if (selected && nextFiles.includes(selected)) await loadFile(selected);
    } catch {
      setMessages((current) => [...current, {
        role: "assistant",
        content: "MiniCoder is unavailable. Try again.",
      }]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <main>
      <aside>
        <header>Files</header>
        <nav>{files.map((file) => (
          <button className={file === selected ? "selected" : ""} onClick={() => void loadFile(file)} key={file}>{file}</button>
        ))}</nav>
        <pre>{content}</pre>
      </aside>
      <section>
        <header>MiniCoder</header>
        <div className="messages">
          {messages.map((message, index) => <p className={message.role} key={index}>{message.content}</p>)}
          {busy && <p className="assistant">Working…</p>}
        </div>
        <form onSubmit={send}>
          <input value={input} onChange={(event) => setInput(event.target.value)} placeholder="Ask MiniCoder" autoFocus />
          <button disabled={busy || !input.trim()}>Send</button>
        </form>
      </section>
    </main>
  );
}
