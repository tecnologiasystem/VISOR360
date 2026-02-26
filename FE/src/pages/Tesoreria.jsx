import React, { useState } from 'react';
import { Button, Card, Typography, Space, Spin, Alert } from 'antd';
import {
  BankOutlined,
  ExportOutlined,
  ReloadOutlined,
  FullscreenOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import './Tesoreria.css';

const { Title, Text } = Typography;

const POWERBI_URL = 'https://app.powerbi.com/view?r=eyJrIjoiOTk3OTIxNjEtNDA2OS00ZDZlLTg1MzMtMDE0NWNkYzBlYTViIiwidCI6IjU4M2VkYjBiLWE4YWQtNGQ5ZS1iNDg2LTE3OGE0ODdjYmMzNyIsImMiOjR9';

const Tesoreria = () => {
  const [loading, setLoading] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const handleIframeLoad = () => {
    setLoading(false);
  };

  const handleRefresh = () => {
    setLoading(true);
    const iframe = document.getElementById('tesoreria-iframe');
    if (iframe) {
      iframe.src = iframe.src;
    }
  };

  const toggleFullscreen = () => {
    const container = document.getElementById('iframe-container');
    if (!document.fullscreenElement) {
      container?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  return (
    <div className="tesoreria-container">
      {/* Header */}
      <div className="tesoreria-header">
        <div className="header-content">
          <div className="header-icon">
            <BankOutlined />
          </div>
          <div className="header-text">
            <Title level={2} className="header-title">Tesorería</Title>
            <Text className="header-subtitle">
              Dashboard de gestión financiera y flujo de caja
            </Text>
          </div>
        </div>

        <Space size="middle" className="header-actions">
          <Button
            icon={<ReloadOutlined />}
            onClick={handleRefresh}
            className="action-btn"
          >
            Actualizar
          </Button>
          <Button
            icon={<FullscreenOutlined />}
            onClick={toggleFullscreen}
            className="action-btn"
          >
            {isFullscreen ? 'Salir' : 'Pantalla Completa'}
          </Button>
          <Button
            type="primary"
            icon={<ExportOutlined />}
            onClick={() => window.open(POWERBI_URL, '_blank')}
            className="primary-btn"
          >
            Abrir en Power BI
          </Button>
        </Space>
      </div>

      {/* Info Alert */}
      <Alert
        message={
          <Space>
            <InfoCircleOutlined />
            <span>Este dashboard se actualiza automáticamente desde Power BI. Si experimenta problemas de visualización, use el botón "Abrir en Power BI".</span>
          </Space>
        }
        type="info"
        showIcon={false}
        className="info-alert"
      />

      {/* Main Content Card */}
      <Card className="tesoreria-card" bordered={false}>
        <div id="iframe-container" className="iframe-container">
          {loading && (
            <div className="loading-overlay">
              <Spin size="large" />
              <Text className="loading-text">Cargando dashboard...</Text>
            </div>
          )}
          <iframe
            id="tesoreria-iframe"
            title="Tesorería PowerBI"
            src={POWERBI_URL}
            onLoad={handleIframeLoad}
            className="powerbi-iframe"
            allowFullScreen
          />
        </div>
      </Card>
    </div>
  );
};

export default Tesoreria;
