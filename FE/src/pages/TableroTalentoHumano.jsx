import React, { useState } from 'react';
import { Card, Row, Col, Select, Tabs } from 'antd';
import { UserOutlined, ToolOutlined } from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './TableroTalentoHumano.css';

const { Option } = Select;

// Componente Modal de Construcción
const ModalConstruccion = ({ onClose }) => (
  <div className="modal-construccion-overlay">
    <div className="modal-construccion">
      <div className="modal-construccion-icon">
        <ToolOutlined />
      </div>
      <h2>En Construcción</h2>
      <p>Este informe está siendo desarrollado y estará disponible próximamente.</p>
      <button className="modal-construccion-btn" onClick={onClose}>
        Entendido
      </button>
    </div>
  </div>
);

const TableroTalentoHumano = () => {
  const [showModal, setShowModal] = useState(true);
  const [selectedMes, setSelectedMes] = useState('Mes 1');

  // Datos de ejemplo para el dashboard
  const rotacionData = {
    mes1: 0,
    mes2: 0,
    mes3: 0,
  };

  const ausentismoData = [
    { fecha: 'Jun 01', value: 0 },
    { fecha: 'Mar 02', value: 0 },
    { fecha: 'Min 03', value: 0 },
    { fecha: 'Jun 04', value: 0 },
    { fecha: 'Mar 05', value: 0 },
    { fecha: 'Sab 06', value: 0 },
    { fecha: 'Dom 07', value: 0 },
  ];

  const capacityData = {
    npl: { real: 0, optimo: 0, disponibilidad: '00%' },
    acc: { real: 0, optimo: 0, disponibilidad: '00%' },
  };

  const climaLaboralData = {
    mes1: { real: 0, optimo: 0 },
    mes2: { real: 0, optimo: 0 },
    mes3: { real: 0, optimo: 0 },
  };

  const tiempoContratacionData = {
    mes1: { asesores: 0, analistas: 0, especialistas: 0 },
    mes2: { asesores: 0, analistas: 0, especialistas: 0 },
    mes3: { asesores: 0, analistas: 0, especialistas: 0 },
  };

  return (
    <div className="rh-board">
      {/* Modal En Construcción */}
      {showModal && <ModalConstruccion onClose={() => setShowModal(false)} />}

      {/* HEADER */}
      <div className="rh-header">
          <div className="header-left">
          <div className="header-blue">
            <h1 className="board-title">RH Board</h1>
            <p className="board-subtitle">Así vamos en la operación</p>
          </div>
          <div className="header-update">
            <span className="update-label">Último día de Actualización</span>
            <span className="update-date">00/00/0000</span>
          </div>
        </div>
      </div>

      {/* Nueva estructura superior de Rotación (cuatro bloques) */}

      <div className="rotacion-header">
        <h2 className="rotacion-title">Rotación</h2>
      </div>

      <div className="rotacion-top">
        <div className="rotacion-item">
          <h4>General</h4>
          <div className="rotacion-subtabs">
            <button className="subtab active">Mes 1</button>
            <button className="subtab">Mes 2</button>
            <button className="subtab">Mes 3</button>
          </div>
          <div className="rotacion-value">000</div>
        </div>

        <div className="rotacion-item">
          <h4>Áreas de la compañía</h4>
          <Select defaultValue="Áreas" style={{ width: '100%' }}>
            <Option value="areas">Áreas</Option>
          </Select>
          <div className="rotacion-value">000</div>
        </div>

        <div className="rotacion-item">
          <h4>Carteras Propias</h4>
          <Select defaultValue="NPL" style={{ width: '100%' }}>
            <Option value="npl">NPL</Option>
          </Select>
          <div className="rotacion-value">000</div>
        </div>

        <div className="rotacion-item">
          <h4>Carteras Administradas</h4>
          <Select defaultValue="ACC" style={{ width: '100%' }}>
            <Option value="acc">ACC</Option>
          </Select>
          <div className="rotacion-value">000</div>
        </div>
      </div>

      <div className="rotacion-separator"></div>

      {/* Sección Inferior: Ausentismo, Capacity, Clima Laboral, Tiempo Contratación */}
      <Row gutter={16} style={{ marginTop: 24 }}>
        {/* === AUSENTISMO === */}
        <section className="ausentismo-container">
          <h2 className="ausentismo-title">Ausentismo</h2>

          <Row gutter={[24, 24]} className="ausentismo-row">
            {/* 🔹 Parte izquierda: Tabs, Selects y línea de tiempo */}
            <Col xs={24} lg={12}>
              <div className="ausentismo-left">
                {/* Tabs + Filtros alineados horizontalmente */}
                <div className="ausentismo-topbar">
                  <div className="ausentismo-tabs">
                    <button className="subtab active">Mes 1</button>
                    <button className="subtab">Mes 2</button>
                    <button className="subtab">Mes 3</button>
                  </div>

                  <div className="ausentismo-selects">
                    <Select defaultValue="Áreas" className="ausentismo-select">
                      <Option value="areas">Áreas</Option>
                    </Select>
                    <Select defaultValue="Carteras" className="ausentismo-select">
                      <Option value="carteras">Carteras</Option>
                    </Select>
                  </div>
                </div>


                {/* Gráfico de línea de tiempo (simplificado) */}
                <div className="timeline-container">
                  <button className="timeline-nav">&lt;</button>

                  <div className="timeline-track">
                    <div className="timeline-item">
                      <span className="day">Lun 01</span>
                      <span className="value">000</span>
                      <div className="tick"></div>
                    </div>
                    <div className="timeline-item">
                      <span className="day">Mar 02</span>
                      <span className="value">000</span>
                      <div className="tick"></div>
                    </div>
                    <div className="timeline-item">
                      <span className="day">Mie 03</span>
                      <span className="value">000</span>
                      <div className="tick"></div>
                    </div>
                    <div className="timeline-item">
                      <span className="day">Jue 04</span>
                      <span className="value">000</span>
                      <div className="tick"></div>
                    </div>
                    <div className="timeline-item">
                      <span className="day">Vie 05</span>
                      <span className="value">000</span>
                      <div className="tick"></div>
                    </div>
                    <div className="timeline-item">
                      <span className="day">Sab 06</span>
                      <span className="value">000</span>
                      <div className="tick"></div>
                    </div>
                    <div className="timeline-item">
                      <span className="day">Dom 07</span>
                      <span className="value">NA</span>
                    </div>
                  </div>

                  <button className="timeline-nav">&gt;</button>
                </div>

                {/* Total */}
                <div className="ausentismo-total">
                  <span className="total-label">Total ausentismos a la fecha:</span>
                  <div className="total-badge">
                    <UserOutlined /> 000
                  </div>
                </div>
              </div>
            </Col>

            {/* 🔹 Parte derecha: Gráfico por áreas y carteras */}
            <Col xs={24} lg={12} className="ausentismo-right-col">
              <div className="grafica-wrapper">
                <h4 className="right-title">Ausentismos por áreas y carteras</h4>

                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={ausentismoData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ddd" />
                    <XAxis
                      dataKey="fecha"
                      tick={{
                        fontSize: 13,
                        fill: "#0023a0",
                        fontWeight: 700,
                        fontStyle: "italic"
                      }}
                    />
                    <YAxis hide />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#0023a0"
                      strokeWidth={2}
                      dot={{ fill: "#ff8c00", r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Col>

          </Row>

          {/* Línea inferior divisoria */}
          <div className="ausentismo-divider"></div>
        </section>
      </Row>

      <Row gutter={[16, 16]} wrap className="section-bottom">
        {/* Capacity */}
        <Col xs={24} md={12} lg={8}>
          <Card className="section-card capacity-card">
            <div className="capacity-header">
              <div className="capacity-title-row">
                <h3 className="card-title">Capacity</h3>

                <div className="capacity-select-group">
                  <Select defaultValue="NPL" className="capacity-select">
                    <Option value="npl">NPL</Option>
                  </Select>
                  <Select defaultValue="ACC" className="capacity-select">
                    <Option value="acc">ACC</Option>
                  </Select>
                </div>

                <span className="capacity-date">A la Fecha:</span>
              </div>
            </div>


            <div className="capacity-top">
              <div className="capacity-icon">
                <UserOutlined />
              </div>

              <div className="capacity-metrics">
                <div className="metric-item">
                  <span className="metric-label">Real</span>
                  <span className="metric-value">000</span>
                </div>
                <div className="metric-item orange">
                  <span className="metric-label">óptimo</span>
                  <span className="metric-value">000</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Disponibilidad</span>
                  <span className="metric-value">00%</span>
                </div>
              </div>
            </div>

            <div className="capacity-footer">
              <h4 className="footer-title">Asesores con ausencias</h4>
              <div className="capacity-table">
                <div className="table-header">
                  <span>Nombre y Apellido</span>
                  <span>Motivo</span>
                  <span>N°</span>
                </div>
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="table-row">
                    <span>Nombre y Apellido</span>
                    <span>Incapacidad</span>
                    <span>00</span>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </Col>


        {/* Clima Laboral */}
        <Col xs={24} md={12} lg={8}>
          <Card className="section-card clima-card">

            <h3 className="clima-title">Clima laboral</h3>

            {/* Tabs */}
            <div className="clima-tabs">
              <button className="clima-tab active">Mes 1</button>
              <button className="clima-tab">Mes 2</button>
              <button className="clima-tab">Mes 3</button>
            </div>

            {/* Valores en dos columnas */}
            <div className="clima-values">

              {/* Caja REAL */}
              <div className="clima-box">
                <span className="clima-label">Real</span>

                <div className="clima-metric real">
                  <span className="clima-number">000</span>
                </div>
              </div>

              {/* Caja OPTIMO */}
              <div className="clima-box">
                <span className="clima-label">óptimo</span>

                <div className="clima-metric optimo">
                  <span className="clima-number">000</span>
                </div>
              </div>

            </div>

          </Card>
        </Col>



        {/* Tiempo promedio contratación */}
        <Col xs={24} md={12} lg={8}>
          <Card className="section-card tiempo-card">

            <h3 className="card-title tiempo-title">Tiempo prom. contratación</h3>

            {/* === TABS CUSTOM COMO LA MAQUETA === */}
            <div className="tiempo-tabs">
              <button className="tiempo-tab active">Mes 1</button>
              <button className="tiempo-tab">Mes 2</button>
              <button className="tiempo-tab">Mes 3</button>
            </div>

            {/* === MÉTRICAS === */}
            <div className="tiempo-metrics">
              <div className="tiempo-row">
                <span className="tiempo-label">Asesores:</span>
                <span className="tiempo-value">{tiempoContratacionData.mes1.asesores}</span>
                <span className="tiempo-unit">Días</span>
              </div>

              <div className="tiempo-row">
                <span className="tiempo-label">Analistas:</span>
                <span className="tiempo-value">{tiempoContratacionData.mes1.analistas}</span>
                <span className="tiempo-unit">Días</span>
              </div>

              <div className="tiempo-row">
                <span className="tiempo-label">Especialistas:</span>
                <span className="tiempo-value">{tiempoContratacionData.mes1.especialistas}</span>
                <span className="tiempo-unit">Días</span>
              </div>
            </div>

          </Card>
        </Col>

      </Row>
    </div >
  );
};

export default TableroTalentoHumano;
