import React, { useState, useRef, useEffect } from 'react';
import { Layout, Avatar, Drawer, Button } from 'antd';
import {
  DashboardOutlined,
  DollarOutlined,
  TeamOutlined,
  LogoutOutlined,
  UserOutlined,
  MenuOutlined,
  CloseOutlined,
  DownOutlined,
  BankOutlined,
  DatabaseOutlined,
  RadarChartOutlined,
  BarChartOutlined,
  RightOutlined,
} from '@ant-design/icons';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './MainLayout.css';

const { Header, Content } = Layout;

const MainLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [openSubmenu, setOpenSubmenu] = useState(null);
  const userMenuRef = useRef(null);
  const navRef = useRef(null);

  // Cerrar menú de usuario al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setUserMenuOpen(false);
      }
      // cerrar submenus si click fuera del nav
      if (navRef.current && !navRef.current.contains(event.target)) {
        setOpenSubmenu(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Construir menú basado en permisos del usuario
  const allMenuItems = [
    {
      key: '/kpi',
      icon: <DashboardOutlined />,
      label: 'Torre de Control',
      permission: 'torre_control',
      children: [
        { key: '/kpi', label: 'Recaudo Operaciones', icon: <DatabaseOutlined /> },
        { key: '/tesoreria', label: 'Tesorería', icon: <BankOutlined /> },
      ],
    },
    {
      key: '/financiero',
      icon: <DollarOutlined />,
      label: 'Análisis Financiero',
      permission: 'financiero',
    },
    {
      key: '/talento',
      icon: <TeamOutlined />,
      label: 'Talento Humano',
      permission: 'recursos_humanos',
      children: [
        { key: '/talento', label: 'RH Board', icon: <BarChartOutlined /> },
        { key: '/radar-talento', label: 'Radar Talento Humano', icon: <RadarChartOutlined /> },
      ],
    },
    {
      key: '/gestion-metas',
      icon: <DollarOutlined />,
      label: 'Gestión de Metas',
      permission: 'gestion_metas',
    },
    {
      key: '/permisos',
      icon: <TeamOutlined />,
      label: 'Permisos',
      permission: 'gestion_usuarios',
    },
  ];

  // Filtrar menú según permisos del usuario
  const menuItems = allMenuItems.filter(item => {
    // Si no tiene permiso definido, dejarlo pasar
    if (!item.permission) return true;
    // Verificar permisos directamente en el objeto user
    return user?.[item.permission] === true;
  });

  const handleMenuClick = ({ key }) => {
    navigate(key);
    setMobileMenuOpen(false);
  };

  const handleLogout = () => {
    setUserMenuOpen(false);
    logout();
    navigate('/login');
  };

  return (
    <Layout className="main-layout">
      {/* Header superior fijo */}
      <Header className="app-header">
        <div className="header-content">
          {/* Logo */}
          <div className="header-brand" onClick={() => navigate('/kpi')}>
            <img src="/img/logo.png" alt="VISOR 360" className="brand-logo-img" />
          </div>

          {/* Navegación Desktop */}
          <nav className="header-nav" ref={navRef}>
            {menuItems.map((item) => (
              item.children ? (
                <div
                  key={item.key}
                  className={`nav-item has-children ${location.pathname.startsWith(item.key) ? 'active' : ''}`}
                  tabIndex={0}
                  onClick={e => { e.preventDefault(); setOpenSubmenu(openSubmenu === item.key ? null : item.key); }}
                  onMouseEnter={() => setOpenSubmenu(item.key)}
                  onMouseLeave={() => setOpenSubmenu(null)}
                  style={{ position: 'relative' }}
                >
                  <span className="nav-icon">{item.icon}</span>
                  <span className="nav-label">{item.label}</span>
                  <DownOutlined className="submenu-arrow" />
                  <div className={`submenu ${openSubmenu === item.key ? 'open' : ''}`} onClick={e => e.stopPropagation()}>
                    {item.children.map((ch) => (
                      <button
                        key={ch.key}
                        className={`submenu-item ${location.pathname === ch.key ? 'active' : ''}`}
                        onClick={(ev) => { ev.stopPropagation(); handleMenuClick({ key: ch.key }); setOpenSubmenu(null); }}
                      >
                        <span className="submenu-icon">{ch.icon}</span>
                        <span className="submenu-label">{ch.label}</span>
                        <RightOutlined className="submenu-chevron" />
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <button
                  key={item.key}
                  className={`nav-item ${location.pathname === item.key ? 'active' : ''}`}
                  onClick={() => { setOpenSubmenu(null); handleMenuClick({ key: item.key }); }}
                >
                  <span className="nav-icon">{item.icon}</span>
                  <span className="nav-label">{item.label}</span>
                </button>
              )
            ))}
          </nav>

          {/* Botón menú móvil */}
          <Button
            className="mobile-menu-btn"
            type="text"
            icon={<MenuOutlined />}
            onClick={() => setMobileMenuOpen(true)}
          />

          {/* Perfil de usuario */}
          <div className="user-menu-container" ref={userMenuRef}>
            <div
              className={`user-profile ${userMenuOpen ? 'active' : ''}`}
              onClick={() => setUserMenuOpen(!userMenuOpen)}
            >
              <Avatar className="user-avatar" icon={<UserOutlined />} size={32} />
              <span className="user-name">{user?.name || 'Usuario'}</span>
              <DownOutlined className={`user-arrow ${userMenuOpen ? 'open' : ''}`} />
            </div>

            {userMenuOpen && (
              <div className="user-dropdown">
                <div className="dropdown-info">
                  <span className="dropdown-name">{user?.name || 'Usuario'}</span>
                  <span className="dropdown-email">{user?.email || user?.username}</span>
                  <span className="dropdown-role">{user?.rol_nombre || user?.rol?.nombre || 'Sin rol'}</span>
                </div>
                <button className="dropdown-logout" onClick={handleLogout}>
                  <LogoutOutlined /> Cerrar Sesión
                </button>
              </div>
            )}
          </div>
        </div>
      </Header>

      {/* Drawer para menú móvil */}
      <Drawer
        title={
          <div className="mobile-drawer-header">
            <span className="mobile-drawer-title">VISOR 360</span>
          </div>
        }
        placement="left"
        onClose={() => setMobileMenuOpen(false)}
        open={mobileMenuOpen}
        className="mobile-nav-drawer"
        closeIcon={<CloseOutlined />}
        width={280}
      >
        <div className="mobile-nav-content">
          <div className="mobile-user-info">
            <Avatar size={48} className="mobile-user-avatar" icon={<UserOutlined />} />
            <div className="mobile-user-details">
              <div className="mobile-user-name">{user?.name || 'Usuario'}</div>
              <div className="mobile-user-role">{user?.rol?.nombre || 'Sin rol'}</div>
            </div>
          </div>

          <nav className="mobile-nav-menu">
            {menuItems.map((item) => (
              <div key={item.key} style={{ width: '100%' }}>
                <button
                  className={`mobile-nav-item ${location.pathname === item.key ? 'active' : ''}`}
                  onClick={() => handleMenuClick({ key: item.key })}
                >
                  <span className="mobile-nav-icon">{item.icon}</span>
                  <span className="mobile-nav-label">{item.label}</span>
                </button>
                {item.children && item.children.map((ch) => (
                  <button
                    key={ch.key}
                    className={`mobile-nav-item mobile-nav-child ${location.pathname === ch.key ? 'active' : ''}`}
                    onClick={() => handleMenuClick({ key: ch.key })}
                    style={{ paddingLeft: 36 }}
                  >
                    <span className="mobile-nav-label">{ch.label}</span>
                  </button>
                ))}
              </div>
            ))}
          </nav>

          <div className="mobile-nav-footer">
            <button className="mobile-logout-btn" onClick={handleLogout}>
              <LogoutOutlined />
              <span>Cerrar Sesión</span>
            </button>
          </div>
        </div>
      </Drawer>

      {/* Contenido principal */}
      <Content className="app-content">
        <Outlet />
      </Content>
    </Layout>
  );
};

export default MainLayout;

