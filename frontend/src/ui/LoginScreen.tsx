import { useState } from "react";
import { BACKEND_URL } from "../game/constants";

interface LoginScreenProps {
  onLogin: (playerId: number, name: string, token: string) => void;
}

export function LoginScreen({ onLogin }: LoginScreenProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const endpoint = isRegister ? "register" : "login";
    const body: any = { username, password };
    if (isRegister) body.name = name;

    try {
      const resp = await fetch(`${BACKEND_URL}/api/auth/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!resp.ok) {
        const data = await resp.json();
        throw new Error(data.detail || "Failed");
      }

      const data = await resp.json();
      onLogin(data.player_id, data.name, data.access_token);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>AURORA</h1>
        <p style={styles.subtitle}>AI-Driven Open World MMORPG</p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <input
            style={styles.input}
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            style={styles.input}
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {isRegister && (
            <input
              style={styles.input}
              placeholder="Character Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          )}

          {error && <p style={styles.error}>{error}</p>}

          <button style={styles.button} type="submit" disabled={loading}>
            {loading ? "..." : isRegister ? "Create Account" : "Login"}
          </button>

          <button
            type="button"
            style={styles.link}
            onClick={() => setIsRegister(!isRegister)}
          >
            {isRegister ? "Already have an account? Login" : "New? Create account"}
          </button>
        </form>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    width: "100vw",
    height: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
    fontFamily: "monospace",
  },
  card: {
    background: "rgba(255,255,255,0.05)",
    border: "1px solid rgba(255,255,255,0.1)",
    borderRadius: 12,
    padding: "40px 32px",
    width: 320,
    textAlign: "center",
  },
  title: {
    color: "#fdd835",
    fontSize: 36,
    margin: 0,
    letterSpacing: 8,
  },
  subtitle: {
    color: "#aaa",
    fontSize: 12,
    marginTop: 4,
    marginBottom: 24,
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: 12,
  },
  input: {
    padding: "10px 14px",
    borderRadius: 6,
    border: "1px solid rgba(255,255,255,0.15)",
    background: "rgba(255,255,255,0.08)",
    color: "#fff",
    fontSize: 14,
    fontFamily: "monospace",
    outline: "none",
  },
  button: {
    padding: "12px",
    borderRadius: 6,
    border: "none",
    background: "#fdd835",
    color: "#1a1a2e",
    fontSize: 14,
    fontWeight: "bold",
    fontFamily: "monospace",
    cursor: "pointer",
    marginTop: 8,
  },
  link: {
    background: "none",
    border: "none",
    color: "#888",
    fontSize: 12,
    cursor: "pointer",
    fontFamily: "monospace",
    textDecoration: "underline",
  },
  error: {
    color: "#ef5350",
    fontSize: 12,
    margin: 0,
  },
};
