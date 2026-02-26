import React, { useState } from 'react';
import { Form, Input, Button, Alert } from 'antd';
import { UserOutlined, LockOutlined, EyeInvisibleOutlined, EyeOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const Login = () => {
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const onFinish = async (values) => {
    setLoading(true);
    setErrorMessage('');
    
    const result = await login(values.username, values.password);
    setLoading(false);

    if (result.success) {
      navigate('/dashboard');
    } else {
      setErrorMessage(result.error || 'Credenciales inválidas.');
    }
  };

  return (
    <div className="login-page">
      {/* Sección izquierda - Branding */}
      <div className="login-branding">
        <div className="branding-content">
          <div className="brand-logo">
            <img src="/img/logo.png" alt="VISOR 360" className="logo-icon-img" />
          </div>
          
          <div className="brand-message">
            <h1 className="brand-title">
              Transforma tus datos en decisiones estratégicas
            </h1>
            <p className="brand-description">
              Monitoreo KPI, Metas, OKR y Logros en tiempo real para impulsar el rendimiento de tu equipo.
            </p>
          </div>

          <div className="brand-features">
            <div className="feature-item">
              <div className="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
                </svg>
              </div>
              <div className="feature-text">
                <span className="feature-title">Análisis en tiempo real</span>
                <span className="feature-desc">Métricas actualizadas al instante</span>
              </div>
            </div>
            <div className="feature-item">
              <div className="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                </svg>
              </div>
              <div className="feature-text">
                <span className="feature-title">Múltiples campañas</span>
                <span className="feature-desc">Gestiona todos tus equipos</span>
              </div>
            </div>
            <div className="feature-item">
              <div className="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="feature-text">
                <span className="feature-title">Reportes detallados</span>
                <span className="feature-desc">Exporta y comparte resultados</span>
              </div>
            </div>
          </div>
        </div>

        <div className="branding-decoration">
          <div className="decoration-circle circle-1"></div>
          <div className="decoration-circle circle-2"></div>
          <div className="decoration-circle circle-3"></div>
        </div>
      </div>

      {/* Sección derecha - Formulario */}
      <div className="login-form-section">
        <div className="form-container">
          <div className="form-header">
            <h2 className="form-title">Bienvenido</h2>
            <p className="form-subtitle">Ingresa tus credenciales para continuar</p>
          </div>

          {errorMessage && (
            <Alert 
              message={errorMessage} 
              type="error" 
              showIcon 
              className="login-alert"
              closable
              onClose={() => setErrorMessage('')}
            />
          )}

          <Form
            name="login"
            initialValues={{ remember: true }}
            onFinish={onFinish}
            layout="vertical"
            requiredMark={false}
            className="login-form"
          >
            <Form.Item
              name="username"
              label="Correo electrónico"
              rules={[{ required: true, message: 'Por favor ingrese su correo' }]}
            >
              <Input 
                prefix={<UserOutlined />} 
                placeholder="ejemplo@correo.com" 
                size="large"
                autoComplete="username"
              />
            </Form.Item>

            <Form.Item
              name="password"
              label="Contraseña"
              rules={[{ required: true, message: 'Por favor ingrese su contraseña' }]}
            >
              <Input.Password 
                prefix={<LockOutlined />} 
                placeholder="••••••••" 
                size="large"
                autoComplete="current-password"
                iconRender={(visible) => (visible ? <EyeOutlined /> : <EyeInvisibleOutlined />)}
              />
            </Form.Item>

            <Form.Item className="form-actions">
              <Button 
                type="primary" 
                htmlType="submit" 
                size="large" 
                loading={loading}
                block
                className="login-btn"
              >
                {loading ? 'Verificando...' : 'Iniciar sesión'}
              </Button>
            </Form.Item>
          </Form>

          <div className="form-footer">
            <div className="footer-divider">
              <span>Powered by</span>
            </div>
            <a 
              href="https://www.systemgroupglobal.com/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="powered-link"
            >
              <img 
                src="/img/powe.png" 
                alt="SystemGroup" 
                className="powered-logo" 
              />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
