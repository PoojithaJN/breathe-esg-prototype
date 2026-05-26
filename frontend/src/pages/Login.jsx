import { useState } from "react";
import api from "../api/client";

function Login() {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("Demo@123");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await api.post("/auth/login/", {
        username,
        password,
      });

      localStorage.setItem("token", response.data.token);
      window.location.href = "/dashboard";
    } catch (err) {
      setError("Invalid login credentials");
    }
  };

  return (
    <div className="page center">
      <form className="card login-card" onSubmit={handleLogin}>
        <h1>Breathe ESG Prototype</h1>
        <p>Analyst Review Login</p>

        {error && <div className="error">{error}</div>}

        <label>Username</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} />

        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button type="submit">Login</button>

        <small>Demo: admin / Demo@123</small>
      </form>
    </div>
  );
}

export default Login;