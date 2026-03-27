import { useCallback, useEffect, useRef, useState } from "react";
import { Engine } from "./game/Engine";
import { HUD } from "./ui/HUD";
import { LoginScreen } from "./ui/LoginScreen";

function App() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const engineRef = useRef<Engine | null>(null);

  const [session, setSession] = useState<{
    playerId: number;
    name: string;
    token: string;
  } | null>(null);

  const handleLogin = useCallback(
    (playerId: number, name: string, token: string) => {
      setSession({ playerId, name, token });
    },
    []
  );

  useEffect(() => {
    if (!session || !canvasRef.current) return;

    const engine = new Engine(session.playerId, session.name, session.token);
    engineRef.current = engine;
    engine.init(canvasRef.current);

    return () => {
      engine.destroy();
      engineRef.current = null;
    };
  }, [session]);

  const handleSendChat = useCallback((text: string) => {
    engineRef.current?.sendChat(text);
  }, []);

  if (!session) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  return (
    <>
      <canvas ref={canvasRef} style={{ display: "block" }} />
      <HUD playerName={session.name} onSendChat={handleSendChat} />
    </>
  );
}

export default App;
