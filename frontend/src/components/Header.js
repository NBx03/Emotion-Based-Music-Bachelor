import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import './Header.css';

function Header() {
  return (
    <header className="header">
      <Link to="/" className="logo">На главную</Link>
      <nav className="header-nav">
        <NavLink to="/history" className="nav-item">История</NavLink>
        <NavLink to="/analytics" className="nav-item">Аналитика</NavLink>
      </nav>
    </header>
  );
}

export default Header;
