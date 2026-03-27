import { useEffect, useState } from "react";

interface HUDProps {
  playerName: string;
  onSendChat: (text: string) => void;
}

interface ChatMsg {
  name: string;
  text: string;
}

export function HUD({ playerName, onSendChat }: HUDProps) {
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMsg[]>([]);
  const [chatOpen, setChatOpen] = useState(false);

  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      setChatMessages((prev) => [...prev.slice(-50), detail]);
    };
    window.addEventListener("game:chat", handler);
    return () => window.removeEventListener("game:chat", handler);
  }, []);

  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    onSendChat(chatInput);
    setChatInput("");
  };

  return (
    <div style={styles.hud}>
      {/* Player info */}
      <div style={styles.playerInfo}>
        <span style={styles.playerName}>{playerName}</span>
        <div style={styles.hpBar}>
          <div style={styles.hpFill} />
        </div>
      </div>

      {/* Controls hint */}
      <div style={styles.controls}>
        WASD to move | Enter to chat
      </div>

      {/* Chat */}
      <div style={styles.chatContainer}>
        <div style={styles.chatMessages}>
          {chatMessages.slice(-8).map((msg, i) => (
            <div key={i} style={styles.chatMsg}>
              <span style={styles.chatName}>{msg.name}:</span> {msg.text}
            </div>
          ))}
        </div>
        <form onSubmit={handleChatSubmit} style={styles.chatForm}>
          <input
            style={styles.chatInput}
            placeholder="Press Enter to chat..."
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onFocus={() => setChatOpen(true)}
            onBlur={() => setChatOpen(false)}
          />
        </form>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  hud: {
    position: "fixed",
    top: 0,
    left: 0,
    width: "100vw",
    height: "100vh",
    pointerEvents: "none",
    fontFamily: "monospace",
    zIndex: 10,
  },
  playerInfo: {
    position: "absolute",
    top: 16,
    left: 16,
    display: "flex",
    alignItems: "center",
    gap: 12,
  },
  playerName: {
    color: "#fdd835",
    fontSize: 14,
    fontWeight: "bold",
  },
  hpBar: {
    width: 120,
    height: 8,
    background: "rgba(0,0,0,0.5)",
    borderRadius: 4,
    overflow: "hidden",
  },
  hpFill: {
    width: "100%",
    height: "100%",
    background: "#4caf50",
    borderRadius: 4,
  },
  controls: {
    position: "absolute",
    top: 16,
    right: 16,
    color: "rgba(255,255,255,0.4)",
    fontSize: 11,
  },
  chatContainer: {
    position: "absolute",
    bottom: 16,
    left: 16,
    width: 320,
    pointerEvents: "auto",
  },
  chatMessages: {
    marginBottom: 4,
  },
  chatMsg: {
    color: "rgba(255,255,255,0.8)",
    fontSize: 12,
    padding: "2px 0",
    textShadow: "0 1px 2px rgba(0,0,0,0.8)",
  },
  chatName: {
    color: "#fdd835",
    fontWeight: "bold",
  },
  chatForm: {
    display: "flex",
  },
  chatInput: {
    flex: 1,
    padding: "8px 12px",
    borderRadius: 6,
    border: "1px solid rgba(255,255,255,0.15)",
    background: "rgba(0,0,0,0.5)",
    color: "#fff",
    fontSize: 12,
    fontFamily: "monospace",
    outline: "none",
  },
};
