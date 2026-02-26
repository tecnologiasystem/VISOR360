import React from "react";
import { Link, NavLink } from "react-router-dom";
import { Avatar, Button } from "antd";
import "./top-header.css";

/**
 * TopHeader:
 * - Mantiene "Sistema QA" a la izquierda
 * - Menú con 3 opciones que usan NavLink (React Router)
 * - Perfil a la derecha
 * - Sticky (fixed at top)
 */

const TopHeader = () => {
  return (
    <header className="qa-top-header">
      <div className="qa-header-left">
        <div className="qa-brand">
          <Link to="/" className="qa-brand-link">
            <div className="qa-brand-title">Sistema QA</div>
          </Link>
        </div>
        <nav className="qa-top-nav" role="navigation" aria-label="Main">
          <NavLink to="/kpi" className="qa-nav-item" activeClassName="qa-nav-item-active" exact>
            Torre de Control
          </NavLink>
          <NavLink to="/financial" className="qa-nav-item" activeClassName="qa-nav-item-active">
            Análisis Financiero
          </NavLink>
          <NavLink to="/hr" className="qa-nav-item" activeClassName="qa-nav-item-active">
            Talento Humano
          </NavLink>
        </nav>
      </div>

      <div className="qa-header-right">
        <Button type="text" className="qa-date-button">November 2025</Button>
        <div className="qa-profile">
          <Avatar style={{ backgroundColor: "#0a58ca" }}>A</Avatar>
          <span className="qa-profile-name">Administrador</span>
        </div>
      </div>
    </header>
  );
};

export default TopHeader;
