import { Link } from "react-router-dom";

function Navbar() {
  const logout = () => {
    localStorage.removeItem("token");
    window.location.href = "/";
  };

  return (
    <nav className="navbar">
      <div className="brand">Breathe ESG</div>

      <div className="nav-links">
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/upload">Upload</Link>
        <Link to="/review">Review</Link>
        <button onClick={logout}>Logout</button>
      </div>
    </nav>
  );
}

export default Navbar;