// Tablero Financiero - Dashboard Unit Economics embebido en VISOR360.
//
// Regla de oro: este tablero NO usa los datos de SQL Server de VISOR360.
// Lee el mismo Excel de siempre, a traves del backend (BE/app/financiero).
// VISOR360 solo presta el login/permisos y el cascaron visual.
//
// Las 4 pestanas replican la app Streamlit original:
//   Business Unit   -> financieroService.getSnapshot
//   Performance     -> financieroService.getPerformance
//   Budget & Goals  -> financieroService.getBudget
//   Read-out        -> "No disponible" (no existe funcion equivalente en el puente)
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Alert, Button, Card, Col, Empty, Form, Row, Select, Spin, Statistic,
  Table, Tabs, Typography, Upload, message,
} from 'antd';
import { UploadOutlined, ReloadOutlined, FileExcelOutlined } from '@ant-design/icons';
import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from 'recharts';
import { useAuth } from '../contexts/AuthContext';
import financieroService from '../services/financieroService';
import './TableroFinanciero.css';

const { Title, Text: Texto } = Typography;

const COLORES = {
  primario: '#2F6FED',
  oscuro: '#0F1E4D',
  secundario: '#B9C4E8',
  positivo: '#16A34A',
  negativo: '#DC2626',
};

const ESTADO_INICIAL = { negocio: 'Consolidated', moneda: 'COP MM', periodo: 'Todos', pais: [], spv: [] };

const fmt = (v, dec = 1) =>
  Number(v ?? 0).toLocaleString('en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec });

function VistaBusinessUnit({ filtros, catalogo, onError }) {
  const [datos, setDatos] = useState(null);
  const [cargando, setCargando] = useState(false);

  const cargar = useCallback(async () => {
    setCargando(true);
    try {
      const { data } = await financieroService.getSnapshot({
        negocio: filtros.negocio, moneda: filtros.moneda, periodo: filtros.periodo,
        pais: filtros.pais, spv: filtros.spv,
      });
      setDatos(data.data ?? data);
    } catch (e) { onError(e); } finally { setCargando(false); }
  }, [filtros, onError]);

  useEffect(() => { cargar(); }, [cargar]);

  const kpis = datos?.kpis ?? {};
  const serie = useMemo(() => {
    const rev = datos?.series?.revenue ?? [];
    const ebitda = datos?.series?.ebitda ?? [];
    return rev.map((p, i) => ({ mes: p.mes, Revenue: p.valor, EBITDA: ebitda[i]?.valor ?? 0 }));
  }, [datos]);

  const waterfall = useMemo(() => {
    if (!datos?.kpis) return [];
    const k = datos.kpis;
    const cogs = k.revenue - k.gross_profit;
    const sga = k.gross_profit - k.ebitda;
    return [
      { nombre: 'Revenue', valor: k.revenue, color: COLORES.primario },
      { nombre: 'COGS', valor: -cogs, color: COLORES.negativo },
      { nombre: 'Gross profit', valor: k.gross_profit, color: COLORES.oscuro },
      { nombre: 'SG&A', valor: -sga, color: COLORES.negativo },
      { nombre: 'EBITDA', valor: k.ebitda, color: COLORES.oscuro },
      { nombre: 'Adj. EBITDA', valor: k.ebitda_adj, color: COLORES.positivo },
    ];
  }, [datos]);

  const filasDetalle = useMemo(
    () => (datos?.detalle ?? []).map((d) => ({
      key: d.linea, linea: d.linea,
      ...Object.fromEntries((d.serie ?? []).map((s) => [s.mes, s.valor])),
      ytd: d.ytd,
    })), [datos],
  );

  const meses = datos?.catalogos?.meses ?? [];
  const columnasDetalle = [
    { title: 'Line', dataIndex: 'linea', key: 'linea', fixed: 'left', width: 220 },
    ...meses.map((m) => ({ title: m, dataIndex: m, key: m, align: 'right', width: 90,
      render: (v) => (v == null ? '-' : fmt(v)) })),
    { title: 'YTD', dataIndex: 'ytd', key: 'ytd', align: 'right', width: 110,
      render: (v) => <strong>{fmt(v)}</strong> },
  ];

  if (cargando && !datos) return <Spin tip="Leyendo el Excel..." />;
  if (!datos) return <Empty description="Sin datos" />;

  return (
    <div>
      <Row gutter={[16, 16]}>
        {[['Revenue', kpis.revenue], ['Gross profit', kpis.gross_profit],
          ['EBITDA', kpis.ebitda], ['Adjusted EBITDA', kpis.ebitda_adj],
          ['Operating profit', kpis.operating_profit]].map(([titulo, valor]) => (
          <Col xs={12} sm={8} md={4} key={titulo}>
            <Card size="small"><Statistic title={titulo} value={fmt(valor)} /></Card>
          </Col>
        ))}
        <Col xs={12} sm={8} md={4}>
          <Card size="small"><Statistic title="EBITDA margin" value={fmt(kpis.ebitda_margin_pct)} suffix="%" /></Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card size="small" title="Income vs costs & expenses by month">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={serie}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="mes" /><YAxis /><Tooltip formatter={(v) => fmt(v)} /><Legend />
                <Bar dataKey="Revenue" fill={COLORES.primario} />
                <Bar dataKey="EBITDA" fill={COLORES.secundario} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card size="small" title="Waterfall - Income statement">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={waterfall}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="nombre" interval={0} angle={-20} textAnchor="end" height={70} />
                <YAxis /><Tooltip formatter={(v) => fmt(v)} />
                <Bar dataKey="valor">{waterfall.map((d) => <Cell key={d.nombre} fill={d.color} />)}</Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      <Card size="small" title="Detailed income statement" style={{ marginTop: 16 }}>
        <Table size="small" pagination={false} scroll={{ x: 'max-content' }}
          columns={columnasDetalle} dataSource={filasDetalle} />
      </Card>

      {(datos.contratos ?? []).length > 0 && (
        <Card size="small" title="Revenue by contract" style={{ marginTop: 16 }}>
          <Row gutter={[8, 8]}>
            {datos.contratos.map((c) => (
              <Col xs={12} md={8} lg={6} key={c.contrato}>
                <div style={{ display: 'flex', justifyContent: 'space-between', background: '#F7F9FC', padding: 8, borderRadius: 4 }}>
                  <Texto>{c.contrato}</Texto><Texto strong>{fmt(c.revenue_ytd)} MM</Texto>
                </div>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {datos.budget && (
        <Card size="small" title="Budget (referencia)" style={{ marginTop: 16 }}>
          <Row gutter={16}>
            <Col span={6}><Statistic title="Revenue YTD" value={fmt(datos.budget.revenue_ytd)} /></Col>
            <Col span={6}><Statistic title="EBITDA YTD" value={fmt(datos.budget.ebitda_ytd)} /></Col>
            <Col span={6}><Statistic title="Revenue anual" value={fmt(datos.budget.revenue_annual)} /></Col>
            <Col span={6}><Statistic title="EBITDA anual" value={fmt(datos.budget.ebitda_annual)} /></Col>
          </Row>
        </Card>
      )}
    </div>
  );
}

function VistaPerformance({ filtros, onError }) {
  const [datos, setDatos] = useState(null);
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    let vivo = true;
    (async () => {
      setCargando(true);
      try {
        const { data } = await financieroService.getPerformance({ negocio: filtros.negocio });
        if (vivo) setDatos(data.data ?? data);
      } catch (e) { onError(e); } finally { if (vivo) setCargando(false); }
    })();
    return () => { vivo = false; };
  }, [filtros.negocio, onError]);

  if (cargando && !datos) return <Spin tip="Leyendo el Excel..." />;
  if (!datos) return <Empty description="Sin datos" />;

  const composicion = datos.composicion ?? [];
  const terceros = datos.terceros ?? [];
  const crxm = datos.crxm ?? [];

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card size="small" title="Cost & expense composition by category">
            <ResponsiveContainer width="100%" height={340}>
              <BarChart data={composicion} layout="vertical" margin={{ left: 40 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" />
                <YAxis type="category" dataKey="Categoria" width={170} />
                <Tooltip formatter={(v) => fmt(v)} /><Legend />
                <Bar dataKey="COGS" stackId="a" fill={COLORES.primario} />
                <Bar dataKey="SGA" stackId="a" fill={COLORES.oscuro} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card size="small" title="Top third-party vendors (Services)">
            <ResponsiveContainer width="100%" height={340}>
              <BarChart data={terceros} layout="vertical" margin={{ left: 40 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" />
                <YAxis type="category" dataKey="Proveedor" width={170} />
                <Tooltip formatter={(v) => fmt(v)} />
                <Bar dataKey="YTD" fill={COLORES.primario} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {crxm.length > 0 && (
        <Card size="small" title="Recovery cost per million (CRxM)" style={{ marginTop: 16 }}>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={crxm.map((r) => ({ campana: r.Campana, YTD: r.YTD }))}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="campana" /><YAxis />
              <Tooltip formatter={(v) => fmt(v, 0)} />
              <Line dataKey="YTD" stroke={COLORES.primario} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      )}

      <Card size="small" title="Detalle por categoria" style={{ marginTop: 16 }}>
        <Table size="small" rowKey="Categoria" pagination={false} dataSource={composicion}
          columns={[
            { title: 'Categoria', dataIndex: 'Categoria' },
            { title: 'COGS', dataIndex: 'COGS', align: 'right', render: (v) => fmt(v) },
            { title: 'SGA', dataIndex: 'SGA', align: 'right', render: (v) => fmt(v) },
          ]}
        />
      </Card>
    </div>
  );
}

function VistaBudget({ filtros, onError }) {
  const [datos, setDatos] = useState(null);
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    let vivo = true;
    (async () => {
      setCargando(true);
      try {
        const { data } = await financieroService.getBudget({ negocio: filtros.negocio });
        if (vivo) setDatos(data.data ?? data);
      } catch (e) { onError(e); } finally { if (vivo) setCargando(false); }
    })();
    return () => { vivo = false; };
  }, [filtros.negocio, onError]);

  if (cargando && !datos) return <Spin tip="Leyendo el Excel..." />;
  if (!datos) return <Empty description="Sin datos" />;

  const anual = datos.anual ?? {};
  const mensual = datos.mensual ?? {};
  const serieMensual = Object.entries(mensual).map(([mes, valores]) => ({
    mes, Revenue: valores?.revenue ?? 0, EBITDA: valores?.ebitda ?? 0,
  }));

  const ETIQUETAS = {
    revenue: 'Operating Income', cos: 'Cost of Services (COS)',
    gross_profit: 'Gross Profit', sga: 'SG&A Expenses',
    ebitda: 'EBITDA', ebitda_adj: 'Adjusted EBITDA',
  };
  const filasAnual = Object.entries(anual).map(([k, v]) => ({ key: k, linea: ETIQUETAS[k] ?? k, valor: v }));

  return (
    <div>
      <Card size="small" title="Annual budget 2026">
        <Table size="small" rowKey="key" pagination={false} dataSource={filasAnual}
          columns={[
            { title: 'Headline line', dataIndex: 'linea' },
            { title: 'Annual budget 2026', dataIndex: 'valor', align: 'right', render: (v) => fmt(v) },
          ]}
        />
      </Card>
      <Card size="small" title="Budget vs actual by month" style={{ marginTop: 16 }}>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={serieMensual}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="mes" /><YAxis /><Tooltip formatter={(v) => fmt(v)} /><Legend />
            <Line dataKey="Revenue" stroke={COLORES.primario} strokeWidth={2} />
            <Line dataKey="EBITDA" stroke={COLORES.oscuro} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </Card>
    </div>
  );
}

function VistaReadOut() {
  return (
    <Card size="small">
      <Empty
        image={Empty.PRESENTED_IMAGE_SIMPLE}
        description={
          <span>
            <strong>Read-out no disponible.</strong>
            <br />
            <Texto type="secondary">
              El texto narrativo con IA no forma parte de esta integracion: el backend de
              VISOR360 solo expone las vistas calculadas. No se inventan cifras.
            </Texto>
          </span>
        }
      />
    </Card>
  );
}

const TableroFinanciero = () => {
  const { user } = useAuth();
  const [filtros, setFiltros] = useState(ESTADO_INICIAL);
  const [catalogo, setCatalogo] = useState(null);
  const [error, setError] = useState(null);
  const [excel, setExcel] = useState(null);
  const [subiendo, setSubiendo] = useState(false);
  const [refresco, setRefresco] = useState(0);

  // Decision acordada: el boton se muestra si el usuario tiene permiso financiero
  // (no existe financiero_admin; no se toca la BD ni el login).
  const puedeSubir = user?.financiero === true;

  const onError = useCallback((e) => {
    const detalle = e?.response?.data?.detail || e?.message || 'Error consultando el tablero.';
    setError(detalle);
  }, []);

  const cargarCatalogo = useCallback(async () => {
    try {
      const { data } = await financieroService.getCatalogo();
      setCatalogo(data.data ?? data);
    } catch (e) { onError(e); }
  }, [onError]);

  const cargarExcel = useCallback(async () => {
    try {
      const { data } = await financieroService.getExcel();
      setExcel(data.data ?? data);
    } catch { /* metadatos: no bloquea la vista */ }
  }, []);

  useEffect(() => { cargarCatalogo(); cargarExcel(); }, [cargarCatalogo, cargarExcel]);

  const subirExcel = async (file) => {
    setSubiendo(true); setError(null);
    try {
      const { data } = await financieroService.subirExcel(file);
      message.success(data?.message || 'Excel actualizado correctamente.');
      await cargarExcel();
      setRefresco((n) => n + 1);
    } catch (e) {
      const detalle = e?.response?.data?.detail || 'No se pudo subir el Excel.';
      setError(detalle); message.error(detalle);
    } finally { setSubiendo(false); }
  };

  const items = [
    { key: 'business', label: 'Business Unit',
      children: <VistaBusinessUnit key={'bu-' + refresco} filtros={filtros} catalogo={catalogo} onError={onError} /> },
    { key: 'performance', label: 'Performance',
      children: <VistaPerformance key={'pf-' + refresco} filtros={filtros} onError={onError} /> },
    { key: 'budget', label: 'Budget & Goals',
      children: <VistaBudget key={'bg-' + refresco} filtros={filtros} onError={onError} /> },
    { key: 'readout', label: 'Read-out', children: <VistaReadOut /> },
  ];

  return (
    <div className="tablero-financiero">
      <Row justify="space-between" align="middle" style={{ marginBottom: 12 }}>
        <Col>
          <Title level={4} style={{ margin: 0 }}>Analisis Financiero - Unit Economics</Title>
          {excel?.existe && (
            <Texto type="secondary"><FileExcelOutlined /> {excel.nombre} · actualizado {excel.actualizado}</Texto>
          )}
        </Col>
        <Col>
          <Row gutter={8}>
            <Col>
              <Button icon={<ReloadOutlined />} onClick={() => setRefresco((n) => n + 1)}>Recargar</Button>
            </Col>
            {puedeSubir && (
              <Col>
                <Upload accept=".xlsx,.xlsm" showUploadList={false} maxCount={1}
                  beforeUpload={(file) => { subirExcel(file); return false; }}>
                  <Button type="primary" icon={<UploadOutlined />} loading={subiendo}>Actualizar Excel</Button>
                </Upload>
              </Col>
            )}
          </Row>
        </Col>
      </Row>

      {!puedeSubir && (
        <Alert type="info" showIcon style={{ marginBottom: 12 }}
          message="Solo lectura: tu usuario no tiene permiso para cargar el Excel del tablero." />
      )}

      {error && (
        <Alert type="error" showIcon closable style={{ marginBottom: 12 }}
          message="Error" description={error} onClose={() => setError(null)} />
      )}

      <Card size="small" style={{ marginBottom: 12 }}>
        <Form layout="vertical">
          <Row gutter={12}>
            <Col xs={24} sm={12} md={5}>
              <Form.Item label="Negocio" style={{ marginBottom: 0 }}>
                <Select value={filtros.negocio} onChange={(v) => setFiltros((f) => ({ ...f, negocio: v }))}
                  options={(catalogo?.negocios ?? ['Consolidated', 'Servicing', 'Master Service', 'NPL']).map((n) => ({ value: n, label: n }))} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} md={4}>
              <Form.Item label="Moneda" style={{ marginBottom: 0 }}>
                <Select value={filtros.moneda} onChange={(v) => setFiltros((f) => ({ ...f, moneda: v }))}
                  options={(catalogo?.monedas ?? ['COP MM', 'USD MM']).map((m) => ({ value: m, label: m }))} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} md={4}>
              <Form.Item label="Periodo" style={{ marginBottom: 0 }}>
                <Select value={filtros.periodo} onChange={(v) => setFiltros((f) => ({ ...f, periodo: v }))}
                  options={(catalogo?.periodos ?? ['Todos', 'Q1', 'Q2', 'Q3']).map((p) => ({ value: p, label: p }))} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} md={5}>
              <Form.Item label="Pais" style={{ marginBottom: 0 }}>
                <Select mode="multiple" allowClear placeholder="Todos" value={filtros.pais}
                  onChange={(v) => setFiltros((f) => ({ ...f, pais: v }))}
                  options={(catalogo?.paises ?? []).map((p) => ({ value: p, label: p }))} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Form.Item label="SPV / Trust" style={{ marginBottom: 0 }}>
                <Select mode="multiple" allowClear placeholder="Todos" value={filtros.spv}
                  onChange={(v) => setFiltros((f) => ({ ...f, spv: v }))}
                  options={(catalogo?.spvs ?? []).map((s) => ({ value: s, label: s }))} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>

      <Tabs items={items} />
    </div>
  );
};

export default TableroFinanciero;
