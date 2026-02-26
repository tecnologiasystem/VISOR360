import React, { useState } from 'react';
import { Card, Row, Col, Tabs } from 'antd';
import { ToolOutlined } from '@ant-design/icons';
import './TableroFinanciero.css';

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

const TableroFinanciero = () => {
  const [showModal, setShowModal] = useState(true);
  const [activeIngresoTab, setActiveIngresoTab] = useState('general');
  const [activeGastoTab, setActiveGastoTab] = useState('general');

  // Datos del Balance Scorecard
  const margenEBITDAData = {
    general: {
      alafecha: { value: '000000000', porcentaje: '00%', desviacion: '00%' },
      forecast: '000000000',
    },
    paises: [
      {
        nombre: 'País 1',
        alafecha: '000000000',
        porcentaje: '00%',
        desviacion: '00%',
        forecast: '000000000',
      },
      {
        nombre: 'País 2',
        alafecha: '000000000',
        porcentaje: '00%',
        desviacion: '00%',
        forecast: '000000000',
      },
      {
        nombre: 'País 3',
        alafecha: '000000000',
        porcentaje: '00%',
        desviacion: '00%',
        forecast: '000000000',
      },
    ],
  };

  const ingresosData = {
    pfg: '000000',
    pfgForecast: '000000000',
    negocios: {
      mes1: { acc: '$0000000', npl: '$0000000' },
      mes2: { acc: '$0000000', npl: '$0000000' },
      mes3: { acc: '$0000000', npl: '$0000000' },
      general: { acc: '$0000000', npl: '$0000000', accDesv: '00%', nplDesv: '00%' },
    },
  };

  const gastosData = {
    general: {
      ejecutado: '$000000',
      presupuesto: '$000000',
      desviacion: '00%',
      totalGastado: '$0000000',
      participacion: '00%',
      gastoAdmin: '$0000000',
      gastoOper: '$0000000',
    },
    mes1: {},
    mes2: {},
    mes3: {},
  };

  const renderPaisCard = (pais) => (
    <Card className="pais-card" key={pais.nombre}>
      <div className="pais-header">
        <span className="pais-label">A la Fecha:</span>
        <span className="pais-value">{pais.alafecha}</span>
      </div>
      <div className="pais-meta">
        <div className="meta-item">
          <span className="meta-label">Porcentaje</span>
          <div className="meta-badge blue">{pais.porcentaje}</div>
        </div>
        <div className="meta-item">
          <span className="meta-label">Desviación</span>
          <div className="meta-badge dark-blue">{pais.desviacion}</div>
        </div>
      </div>
      <div className="pais-forecast">
        <span className="forecast-label">Forecast</span>
        <span className="forecast-value">{pais.forecast}</span>
      </div>
    </Card>
  );

  return (
    <div className="tablero-financiero">
      {/* Modal En Construcción */}
      {showModal && <ModalConstruccion onClose={() => setShowModal(false)} />}
      
      {/* Header */}
      <div className="tablero-header">
        <div className="header-banner">
          <h1>Balance Score Card</h1>
          <p>Así vamos como empresa</p>
        </div>

        <div className="header-date">
          <span className="update-label-block">
            <span>Último día</span>
            <span>de Actualización:</span>
          </span>
          <span className="update-date">00/00/0000</span>
        </div>

      </div>


      {/* Margen EBITDA Section */}
      <div className="margen-ebitda-section">
        <h2 className="section-title">Margen EBITDA</h2>

        <div className="ebitda-grid-maqueta">
          {/* === General === */}
          <div className="ebitda-general">
            
            <h3>General</h3>

            <div className="fila-horizontal">
              {/* Columna izquierda */}
              <div className="columna-datos">
                <div className="fila-datos">
                  <div className="box">
                    <p className="label">A la Fecha:</p>
                    <p className="value">{margenEBITDAData.general.alafecha.value}</p>
                  </div>
                  <div className="box right">
                    <p className="label">Porc. Cump</p>
                    <p className="value">{margenEBITDAData.general.alafecha.porcentaje}</p>
                  </div>
                </div>

                <div className="forecast">
                  <p className="label">Forecast</p>
                  <p className="value">{margenEBITDAData.general.forecast}</p>
                </div>
              </div>

              {/* Caja azul lateral */}
              <div className="desviacion-box-lateral">
                <p className="label">Desviación</p>
                <p className="value">{margenEBITDAData.general.alafecha.desviacion}</p>
              </div>
            </div>
          </div>

          {/* === Países === */}
          {[1, 2, 3, 4, 5, 6].map((num) => (
            <div key={num} className="pais-maqueta">
              <h3>País {num}</h3>

              <div className="fila-horizontal">
                {/* 🔹 Contenedor A la Fecha / Porcentaje con borde azul */}
                <div className="columna-datos">
                  <div className="bloque-superior">
                    <div className="fila-datos">
                      <div className="box">
                        <p className="label">A la Fecha:</p>
                        <p className="value">000000000</p>
                      </div>
                      <div className="box right">
                        <p className="label">Porcentaje</p>
                        <p className="value">00%</p>
                      </div>
                    </div>
                  </div>

                  {/* 🔸 Forecast fuera del borde azul */}
                  <div className="forecast">
                    <p className="label">Forecast</p>
                    <p className="value">000000000</p>
                  </div>
                </div>

                {/* 🔹 Caja azul lateral */}
                <div className="desviacion-box-lateral">
                  <p className="label">Desviación</p>
                  <p className="value">00%</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>



      {/* Ingresos y Gastos */}
      <Row gutter={16} style={{ marginTop: 24 }}>
        {/* Ingresos */}
        <Col xs={24} md={12}>
          <div className="section-container">
            <h2 className="section-title-inline">Ingresos</h2>

            <div className="ingresos-tabs ingresos-tabs-compacto">
              {/* 🔹 Flecha izquierda */}
              <span className="arrow-left">&lt;</span>

              {/* 🔹 Tabs de Ant Design */}
              <Tabs
                className='paises'
                activeKey={activeIngresoTab}
                onChange={setActiveIngresoTab}
                size="small"
                items={[
                  { key: 'general', label: 'General' },
                  { key: 'pais1', label: 'País 1' },
                  { key: 'pais2', label: 'País 2' },
                  { key: 'pais3', label: 'País 3' },
                  { key: 'pais4', label: 'País 4' },
                ]}
              />

              {/* 🔹 Flecha derecha */}
              <span className="arrow-right">&gt;</span>
            </div>


            <div className="pfg-section">
              <div className="pfg-group">
                <span className="pfg-label">PFG:</span>
                <span className="pfg-value">{ingresosData.pfg}</span>
                <span className="pfg-indicator"></span>
              </div>

              <div className="pfg-group">
                <span className="pfg-label">PFG Forecasta:</span>
                <span className="pfg-value">{ingresosData.pfgForecast}</span>
              </div>
            </div>

            <div className="linea-naranja-ingresos"></div>



            <div className="negocios-section">
              <h3 className="negocios-title">Negocios</h3>
              <Tabs
                className="negocios-tabs"
                defaultActiveKey="general"
                size="small"
                items={[
                  { key: 'mes1', label: 'Mes 1' },
                  { key: 'mes2', label: 'Mes 2' },
                  { key: 'mes3', label: 'Mes 3' },
                  { key: 'general', label: <span className="t-general">General</span> },
                ]}
              />


              {/* === ACC y NPL uno al lado del otro, como en la maqueta === */}
              <div className="negocios-metricas">
                {/* === ACC === */}
                <div className="negocio-card acc-card">
                  <div className="negocio-header">Logrado</div>
                  <div className="negocio-label">
                    ACC:
                    <span className="negocio-value">{ingresosData.negocios.general.acc}</span>
                  </div>

                  {activeIngresoTab === 'general' && (
                    <div className="negocio-footer">
                      <div className="desv-forecast-row">
                        {/* Desviación (naranja) */}
                        <div className="desv-box">
                          <span className="desv-label">Desviación</span>
                          <div className="negocio-desviacion orange">
                            {ingresosData.negocios.general.accDesv}
                          </div>
                        </div>

                        {/* Forecast (azul) */}
                        <div className="forecast-box">
                          <span className="forecast-label">Forecast</span>
                          <div className="negocio-forecast">
                            {ingresosData.negocios.general.acc}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* === NPL === */}
                <div className="negocio-card npl-card">
                  <div className="negocio-header">Logrado</div>
                  <div className="negocio-label">
                    NPL:
                    <span className="negocio-value">{ingresosData.negocios.general.npl}</span>
                  </div>

                  {activeIngresoTab === 'general' && (
                    <div className="negocio-footer">
                      <div className="desv-forecast-row">
                        {/* Desviación (naranja) */}
                        <div className="desv-box">
                          <span className="desv-label">Desviación</span>
                          <div className="negocio-desviacion orange">
                            {ingresosData.negocios.general.nplDesv}
                          </div>
                        </div>

                        {/* Forecast (azul) */}
                        <div className="forecast-box">
                          <span className="forecast-label">Forecast</span>
                          <div className="negocio-forecast">
                            {ingresosData.negocios.general.npl}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>


            </div>
          </div>
        </Col>

        {/* Gastos */}
        <Col xs={24} md={12}>
          <div className="section-container">
            <h2 className="section-title-inline">Gastos</h2>

            <div className="gastos-tabs">
              <span className="arrow-left">&lt;</span>

              <div className="gastos-tabs-inner">
                <Tabs
                  activeKey={activeGastoTab}
                  onChange={setActiveGastoTab}
                  size="small"
                  items={[
                    { key: 'general', label: 'General ' },
                    { key: 'mes1', label: 'Mes 1' },
                    { key: 'mes2', label: 'Mes 2' },
                    { key: 'mes3', label: 'Mes 3' },
                    { key: 'mes4', label: 'Mes 4' }
                  ]}
                />
              </div>

              <span className="arrow-right">&gt;</span>
            </div>


            <div className="gastos-comparacion">
              <div className="gastos-top-row">
                {/* Gasto Ejecutado */}
                <div className="gasto-card ejecutado">
                  <div className="gasto-label">Gasto Ejecutado</div>
                  <div className="gasto-value">{gastosData.general.ejecutado}</div>
                </div>

                {/* VS centrado */}
                <div className="vs-badge">VS</div>

                {/* Presupuesto */}
                <div className="gasto-card presupuesto">
                  <div className="gasto-label">Presupuesto</div>
                  <div className="gasto-value">{gastosData.general.presupuesto}</div>
                </div>

                {/* Desviación */}
                <div className="gasto-card desviacion">
                  <div className="gasto-label">Desviación</div>
                  <div className="gasto-value blue">{gastosData.general.desviacion}</div>
                </div>
              </div>
            </div>


            <Row gutter={16} className='gastos-totales-row'>
              <Col span={12}>
                <Card className="total-card">
                  <div className="total-content">
                    <span className="total-label">
                      Total gastado en el año hasta la fecha.
                    </span>
                    <span className="total-value">$0000000</span>
                  </div>
                </Card>
              </Col>

              <Col span={12}>
                <Card className="total-card">
                  <div className="total-content participacion-gasto">
                    <span className="total-label">
                      Participación en el gasto
                    </span>
                    <span className="total-value yellow">00%</span>
                  </div>
                </Card>
              </Col>
            </Row>

            {/* 🔶 Línea naranja debajo de totales */}
            <div className="linea-naranja-inferior"></div>

            {/* === Gastos Detallados (Administrativo / Operativo) === */}
            <Row gutter={16} className="gastos-detallados-row">
              <Col span={12}>
                <Card className="detalle-card">
                  <div className="detalle-content">
                    <span className="detalle-label">
                      Gasto Administrativo <br />
                      <span className="detalle-sub">(Overhed Asdir)</span>
                    </span>
                    <span className="detalle-value">{gastosData.general.gastoAdmin}</span>
                  </div>
                </Card>
              </Col>

              <Col span={12}>
                <Card className="detalle-card">
                  <div className="detalle-content">
                    <span className="detalle-label">
                      Gasto Operativo <br />
                      <span className="detalle-sub">(Costo directo)</span>
                    </span>
                    <span className="detalle-value">{gastosData.general.gastoOper}</span>
                  </div>
                </Card>
              </Col>
            </Row>

          </div>
        </Col>
      </Row>
    </div>
  );
};

export default TableroFinanciero;
