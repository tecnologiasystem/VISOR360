import React, { useState, useEffect, useMemo } from 'react';
import { Select, Spin, message, Tooltip } from 'antd';
import {
    UserOutlined,
    DollarCircleOutlined,
    WomanOutlined,
    ManOutlined,
    CalendarOutlined,
} from '@ant-design/icons';
import './RadarTalento.css';
import api from '../api';

const { Option } = Select;

// Formateo de moneda según el país
const formatMoney = (value, pais) => {
    if (!value) return '$0';
    
    let locale = 'es-CO';
    let currency = 'COP';
    
    if (pais === 'PERU' || pais === 'PER') {
        locale = 'es-PE';
        currency = 'PEN';
    } else if (pais === 'PANAMA' || pais === 'PAN') {
        locale = 'es-PA';
        currency = 'PAB';
    }
    
    return new Intl.NumberFormat(locale, {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
};

// Formateo compacto de moneda (K para miles, M para millones)
const formatMoneyCompact = (value, pais) => {
    if (!value || value === 0) return '$0';
    
    let symbol = '$';
    if (pais === 'PERU' || pais === 'PER') {
        symbol = 'S/';
    } else if (pais === 'PANAMA' || pais === 'PAN') {
        symbol = 'B/.';
    }
    
    const absValue = Math.abs(value);
    
    if (absValue >= 1000000) {
        // Millones
        return `${symbol}${(value / 1000000).toFixed(1)}M`;
    } else if (absValue >= 1000) {
        // Miles
        return `${symbol}${(value / 1000).toFixed(1)}K`;
    } else {
        // Menor a mil
        return `${symbol}${value.toFixed(0)}`;
    }
};

// Formateo de números
const formatNumber = (value) => {
    if (!value) return '0';
    return new Intl.NumberFormat('es-CO').format(value);
};

const RadarTalento = () => {
    // Estados de filtros
    const [pais, setPais] = useState(null); // null = todos
    const [mes, setMes] = useState(10); // Octubre por defecto
    const [anio, setAnio] = useState(2025); // 2025 por defecto
    
    // Estado de datos
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState(null);
    
    // Estado para responsive
    const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

    useEffect(() => {
        const onResize = () => setIsMobile(window.innerWidth <= 768);
        window.addEventListener("resize", onResize);
        return () => window.removeEventListener("resize", onResize);
    }, []);

    // Cargar datos cuando cambien los filtros
    useEffect(() => {
        cargarDatos();
    }, [pais, mes, anio]);

    const cargarDatos = async () => {
        setLoading(true);
        try {
            const params = {};
            if (pais) params.pais = pais;
            if (mes) params.mes = mes;
            if (anio) params.anio = anio;
            
            const response = await api.get('/planta-activa/resumen', { params });
            
            if (response.data?.success) {
                setData(response.data.data);
            } else {
                message.error('Error al cargar datos');
            }
        } catch (error) {
            console.error('Error cargando radar talento:', error);
            message.error('Error al conectar con el servidor');
        } finally {
            setLoading(false);
        }
    };

    // Procesar géneros para los cards
    const procesarGeneros = () => {
        if (!data?.generos) return { mujeres: 0, hombres: 0, percMujeres: 0, percHombres: 0 };
        
        const total = data.personal_activo;
        const mujeres = data.generos['F'] || data.generos['f'] || data.generos['Femenino'] || 0;
        const hombres = data.generos['M'] || data.generos['m'] || data.generos['Masculino'] || 0;
        
        return {
            mujeres,
            hombres,
            percMujeres: total > 0 ? ((mujeres / total) * 100).toFixed(1) : 0,
            percHombres: total > 0 ? ((hombres / total) * 100).toFixed(1) : 0
        };
    };

    // Datos procesados para mostrar
    const resumenTop = useMemo(() => {
        if (!data) return [];
        
        const generos = procesarGeneros();
        
        return [
            {
                key: 'personal',
                titulo: 'Personal Activo',
                valor: formatNumber(data.personal_activo),
                icono: <UserOutlined />,
            },
            {
                key: 'costo',
                titulo: 'Costo recurso humano',
                valor: formatMoney(data.costo_recurso_humano, pais),
                icono: <DollarCircleOutlined />,
            },
            {
                key: 'activas',
                titulo: 'Activas',
                valor: formatNumber(generos.mujeres),
                icono: <WomanOutlined />,
                extra: `${generos.percMujeres}%`,
            },
            {
                key: 'activos',
                titulo: 'Activos',
                valor: formatNumber(generos.hombres),
                icono: <ManOutlined />,
                extra: `${generos.percHombres}%`,
            },
            {
                key: 'edad',
                titulo: 'Edad prom.',
                valor: Math.round(data.edad_promedio || 0),
                icono: <CalendarOutlined />,
            },
        ];
    }, [data]);

    // Activos por unidad
    const activosUnidad = useMemo(() => {
        if (!data?.por_unidad || data.por_unidad.length === 0) return [];
        
        // Agrupar por categorías principales
        const categorias = {
            ACC: { cantidad: 0 },
            NPL: { cantidad: 0 },
            STAFF: { cantidad: 0 },
            OTROS: { cantidad: 0 }
        };
        
        const total = data.por_unidad.reduce((sum, u) => sum + u.cantidad, 0);
        
        data.por_unidad.forEach(u => {
            const unidadUpper = (u.unidad || '').toUpperCase();
            if (unidadUpper.includes('ACC') || unidadUpper.includes('PRODUCTO ACC')) {
                categorias.ACC.cantidad += u.cantidad;
            } else if (unidadUpper.includes('NPL') || unidadUpper.includes('PRODUCTO NPL')) {
                categorias.NPL.cantidad += u.cantidad;
            } else if (unidadUpper.includes('STAFF')) {
                categorias.STAFF.cantidad += u.cantidad;
            } else {
                categorias.OTROS.cantidad += u.cantidad;
            }
        });
        
        return [
            { key: 'acc', label: 'ACC', valor: formatNumber(categorias.ACC.cantidad), porcentaje: `${total > 0 ? Math.round((categorias.ACC.cantidad / total) * 100) : 0}%` },
            { key: 'npl', label: 'NPL', valor: formatNumber(categorias.NPL.cantidad), porcentaje: `${total > 0 ? Math.round((categorias.NPL.cantidad / total) * 100) : 0}%` },
            { key: 'staff', label: 'STAFF', valor: formatNumber(categorias.STAFF.cantidad), porcentaje: `${total > 0 ? Math.round((categorias.STAFF.cantidad / total) * 100) : 0}%` },
            { key: 'otros', label: 'OTROS', valor: formatNumber(categorias.OTROS.cantidad), porcentaje: `${total > 0 ? Math.round((categorias.OTROS.cantidad / total) * 100) : 0}%` },
        ];
    }, [data]);

    // Datos de tipo de contrato
    const datosContrato = useMemo(() => {
        if (!data?.por_contrato) return [];
        const total = data.por_contrato.reduce((sum, c) => sum + c.cantidad, 0);
        return data.por_contrato.map(c => ({
            label: c.tipo,
            valor: c.cantidad,
            porcentaje: `${total > 0 ? Math.round((c.cantidad / total) * 100) : 0}%`
        }));
    }, [data]);

    // Datos de departamento
    const datosDepartamento = useMemo(() => {
        if (!data?.por_departamento) return [];
        return data.por_departamento.slice(0, 10).map(d => ({
            departamento: d.departamento,
            cantidad: d.cantidad,
            salario: d.salario
        }));
    }, [data]);

    // Datos de cargos
    const datosCargos = useMemo(() => {
        if (!data?.por_cargo) return [];
        return data.por_cargo.slice(0, 10).map(c => ({
            cargo: c.cargo,
            cantidad: c.cantidad
        }));
    }, [data]);

    // Datos de tipo de cargo
    const datosTipoCargo = useMemo(() => {
        if (!data?.por_tipo_cargo) return [];
        const total = data.por_tipo_cargo.reduce((sum, t) => sum + t.cantidad, 0);
        return data.por_tipo_cargo.map(t => ({
            tipo: t.tipo,
            cantidad: t.cantidad,
            porcentaje: total > 0 ? Math.round((t.cantidad / total) * 100) : 0
        }));
    }, [data]);

    // Máximo valor para escalar barras
    const maxContrato = useMemo(() => {
        if (!datosContrato.length) return 1;
        return Math.max(...datosContrato.map(d => d.valor));
    }, [datosContrato]);

    const maxDepartamento = useMemo(() => {
        if (!datosDepartamento.length) return 1;
        return Math.max(...datosDepartamento.map(d => d.cantidad));
    }, [datosDepartamento]);

    // Meses disponibles
    const mesesDisponibles = [
        { value: 1, label: 'Enero' },
        { value: 2, label: 'Febrero' },
        { value: 3, label: 'Marzo' },
        { value: 4, label: 'Abril' },
        { value: 5, label: 'Mayo' },
        { value: 6, label: 'Junio' },
        { value: 7, label: 'Julio' },
        { value: 8, label: 'Agosto' },
        { value: 9, label: 'Septiembre' },
        { value: 10, label: 'Octubre' },
        { value: 11, label: 'Noviembre' },
        { value: 12, label: 'Diciembre' },
    ];

    // Años disponibles
    const aniosDisponibles = [2024, 2025, 2026];

    return (
        <div className="radar-talento-page">
            <div className="radar-talento-container">

                {/* === ENCABEZADO SUPERIOR === */}
                <div className="rt-header">
                    <h1 className="rt-title">Radar de Talento Humano</h1>

                    <div className="rt-filtros">
                        <Select
                            value={pais}
                            onChange={setPais}
                            className="rt-select"
                            placeholder="Seleccionar país"
                            allowClear
                            getPopupContainer={() => document.body}
                            popupClassName="rt-select-popup"
                        >
                            <Option value="COLOMBIA">Colombia</Option>
                            <Option value="PERU">Perú</Option>
                            <Option value="PANAMA">Panamá</Option>
                        </Select>

                        <Select
                            value={mes}
                            onChange={setMes}
                            className="rt-select"
                            placeholder="Mes"
                            getPopupContainer={() => document.body}
                            popupClassName="rt-select-popup"
                        >
                            {mesesDisponibles.map(m => (
                                <Option key={m.value} value={m.value}>{m.label}</Option>
                            ))}
                        </Select>

                        <Select
                            value={anio}
                            onChange={setAnio}
                            className="rt-select"
                            placeholder="Año"
                            getPopupContainer={() => document.body}
                            popupClassName="rt-select-popup"
                        >
                            {aniosDisponibles.map(a => (
                                <Option key={a} value={a}>{a}</Option>
                            ))}
                        </Select>
                    </div>
                </div>

                {loading ? (
                    <div className="rt-loading">
                        <Spin size="large" />
                        <p>Cargando datos...</p>
                    </div>
                ) : (
                    <>
                        {/* ===== CONTENEDORES SUPERIORES AZULES ===== */}
                        <div className="rt-summary">

                            {/* Grupo 1: Personal + Costo */}
                            <div className="rt-card group-large">
                                <div className="rt-item">
                                    <span className="rt-title-small">{resumenTop[0]?.titulo}</span>
                                    <div className="rt-value-row">
                                        <span className="rt-icon">{resumenTop[0]?.icono}</span>
                                        <span className="rt-value">{resumenTop[0]?.valor}</span>
                                    </div>
                                </div>

                                <div className="rt-separator"></div>

                                <div className="rt-item">
                                    <span className="rt-title-small">{resumenTop[1]?.titulo}</span>
                                    <div className="rt-value-row">
                                        <span className="rt-icon">{resumenTop[1]?.icono}</span>
                                        <span className="rt-value">{resumenTop[1]?.valor}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Grupo 2: Activas + Activos */}
                            <div className="rt-card group-medium">
                                <div className="rt-item">
                                    <span className="rt-title-small">{resumenTop[2]?.titulo}</span>
                                    <div className="rt-value-row">
                                        <span className="rt-icon">{resumenTop[2]?.icono}</span>
                                        <span className="rt-value">{resumenTop[2]?.valor}</span>
                                        <span className="rt-badge">{resumenTop[2]?.extra}</span>
                                    </div>
                                </div>

                                <div className="rt-separator"></div>

                                <div className="rt-item">
                                    <span className="rt-title-small">{resumenTop[3]?.titulo}</span>
                                    <div className="rt-value-row">
                                        <span className="rt-icon">{resumenTop[3]?.icono}</span>
                                        <span className="rt-value">{resumenTop[3]?.valor}</span>
                                        <span className="rt-badge">{resumenTop[3]?.extra}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Grupo 3: Edad */}
                            <div className="rt-card group-small">
                                <div className="rt-item">
                                    <span className="rt-title-small">{resumenTop[4]?.titulo}</span>
                                    <div className="rt-value-row">
                                        <span className="rt-icon">{resumenTop[4]?.icono}</span>
                                        <span className="rt-value">{resumenTop[4]?.valor}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* ===== ACTIVOS POR UNIDAD ===== */}
                        <div className="rt-section-title">Activos por Unidad</div>

                        <div className="unidad-grid">
                            {activosUnidad.map((item) => (
                                <div key={item.key} className="unidad-card">
                                    <div className="unidad-row">
                                        <span className="unidad-etiqueta">{item.label}</span>
                                        <span className="unidad-valor">{item.valor}</span>
                                        <span className="unidad-separador"></span>
                                        <span className="unidad-porcentaje">{item.porcentaje}</span>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* ===== BLOQUES INFERIORES ===== */}
                        <div className="rt-grid">

                            {/* COLUMNA IZQUIERDA */}
                            <div className="rt-grid-left">

                                {/* Tipo de Contrato */}
                                <div className="rt-block">
                                    <h3 className="rt-block-title">Tipo de Contrato</h3>
                                    <div className="rt-chart-area">
                                        {(() => {
                                            const max = Math.max(...datosContrato.map(d => d.valor));
                                            const scale = 200;
                                            const baseY = 240;
                                            const sectionWidth = 900 / datosContrato.length;

                                            const linePoints = datosContrato.map((d, i) => {
                                                const x = sectionWidth * i + sectionWidth / 2;
                                                const y = baseY - (d.valor / max) * scale;
                                                return `${x},${y}`;
                                            }).join(" ");

                                            return (
                                                <svg viewBox="0 0 900 320" preserveAspectRatio="xMidYMid meet" className="rt-chart-svg">
                                                    {/* Línea naranja */}
                                                    <polyline
                                                        fill="none"
                                                        stroke="#f6a52d"
                                                        strokeWidth="3"
                                                        points={linePoints}
                                                    />

                                                    {datosContrato.map((d, i) => {
                                                        const cx = sectionWidth * i + sectionWidth / 2;
                                                        const barHeight = (d.valor / max) * scale;
                                                        const y = baseY - barHeight;

                                                        return (
                                                            <Tooltip 
                                                                key={i}
                                                                title={
                                                                    <div style={{ textAlign: 'center' }}>
                                                                        <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '4px' }}>
                                                                            {d.label}
                                                                        </div>
                                                                        <div style={{ fontSize: '16px', fontWeight: '800' }}>
                                                                            {d.valor} empleados
                                                                        </div>
                                                                        <div style={{ fontSize: '14px', color: '#f6a52d' }}>
                                                                            {d.porcentaje}
                                                                        </div>
                                                                    </div>
                                                                }
                                                                color="#002a8d"
                                                            >
                                                                <g style={{ cursor: 'pointer' }}>
                                                                    {/* Porcentaje arriba */}
                                                                    <text
                                                                        x={cx}
                                                                        y={y - 16}
                                                                        style={{
                                                                            fill: "#002a8d",
                                                                            fontSize: "22px",
                                                                            fontWeight: "800",
                                                                            textAnchor: "middle"
                                                                        }}
                                                                    >
                                                                        {d.porcentaje}
                                                                    </text>

                                                                    {/* Punto de línea */}
                                                                    <circle cx={cx} cy={y} r="4" fill="#ccc" />

                                                                    {/* Barra azul */}
                                                                    <rect
                                                                        x={cx - 35}
                                                                        y={y}
                                                                        width="70"
                                                                        height={barHeight}
                                                                        fill="#002a8d"
                                                                        rx="5"
                                                                    />

                                                                    {/* Área invisible más grande para mejor interacción */}
                                                                    <rect
                                                                        x={cx - 50}
                                                                        y={y - 20}
                                                                        width="100"
                                                                        height={barHeight + 20}
                                                                        fill="transparent"
                                                                    />

                                                                    {/* Label inferior */}
                                                                    <text
                                                                        x={cx}
                                                                        y={300}
                                                                        style={{
                                                                            fill: "#002a8d",
                                                                            fontSize: "16px",
                                                                            fontWeight: "600",
                                                                            textAnchor: "middle"
                                                                        }}
                                                                    >
                                                                        {d.label}
                                                                    </text>
                                                                </g>
                                                            </Tooltip>
                                                        );
                                                    })}
                                                </svg>
                                            );
                                        })()}
                                    </div>
                                </div>

                                {/* Distribución por Cargo */}
                                <div className="rt-block">
                                    <h3 className="rt-block-title">Distribución por Cargo</h3>
                                    <div className="rt-chart-placeholder rt-chart-placeholder--tall">
                                        {datosCargos.length > 0 ? (
                                            (() => {
                                                const maxCantidad = Math.max(...datosCargos.map(c => c.cantidad));
                                                const labelWidth = 400;
                                                const barAreaWidth = 450;
                                                const totalWidth = labelWidth + barAreaWidth;
                                                const rowHeight = 65;
                                                const headerHeight = 60;
                                                
                                                return (
                                                    <svg width="100%" height="100%" viewBox={`0 0 ${totalWidth} ${datosCargos.length * rowHeight}`} preserveAspectRatio="xMinYMin meet" style={{ minHeight: '400px' }}>
                                                        {datosCargos.map((cargo, i) => {
                                                            const y = i * rowHeight;
                                                            const barWidth = (cargo.cantidad / maxCantidad) * barAreaWidth;
                                                            const minWidth = 50;
                                                            const finalWidth = Math.max(barWidth, minWidth);

                                                            return (
                                                                <g key={i}>
                                                                    {/* NOMBRE DEL CARGO */}
                                                                    <text
                                                                        x="20"
                                                                        y={y + 35}
                                                                        style={{ fill: "#002a8d", fontSize: "20px", fontWeight: "600" }}
                                                                    >
                                                                        {cargo.cargo && cargo.cargo.length > 40 ? cargo.cargo.substring(0, 37) + '...' : (cargo.cargo || 'Sin cargo')}
                                                                    </text>

                                                                    {/* LÍNEA PUNTEADA */}
                                                                    <line 
                                                                        x1={labelWidth} 
                                                                        y1={y + 28} 
                                                                        x2={labelWidth + finalWidth} 
                                                                        y2={y + 28} 
                                                                        stroke="#ccc" 
                                                                        strokeWidth="1" 
                                                                        strokeDasharray="4,4" 
                                                                    />

                                                                    {/* BARRA */}
                                                                    <rect 
                                                                        x={labelWidth} 
                                                                        y={y + 10} 
                                                                        width={finalWidth} 
                                                                        height={42} 
                                                                        rx="6" 
                                                                        fill="#f6a52d" 
                                                                    />

                                                                    {/* CANTIDAD */}
                                                                    <text
                                                                        x={labelWidth + finalWidth / 2}
                                                                        y={y + 38}
                                                                        style={{ fill: "white", fontSize: "18px", fontWeight: "800", textAnchor: "middle" }}
                                                                    >
                                                                        {cargo.cantidad}
                                                                    </text>
                                                                </g>
                                                            );
                                                        })}
                                                    </svg>
                                                );
                                            })()
                                        ) : (
                                            <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                                                No hay datos disponibles
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Tipo de Cargo */}
                                <div className="rt-block">
                                    <h3 className="rt-block-title">Tipo de Cargo</h3>
                                    <div className="rt-chart-placeholder">
                                        {datosTipoCargo.length > 0 ? (
                                            (() => {
                                                const maxCantidad = Math.max(...datosTipoCargo.map(t => t.cantidad));
                                                const labelWidth = 350;
                                                const barAreaWidth = 600;
                                                const totalWidth = labelWidth + barAreaWidth + 100;
                                                const rowHeight = 75;
                                                
                                                return (
                                                    <svg width="100%" height="100%" viewBox={`0 0 ${totalWidth} ${datosTipoCargo.length * rowHeight}`} preserveAspectRatio="xMinYMin meet" style={{ minHeight: '350px' }}>
                                                        {datosTipoCargo.map((tipo, i) => {
                                                            const y = i * rowHeight;
                                                            const barWidth = (tipo.cantidad / maxCantidad) * barAreaWidth;
                                                            const minWidth = 100;
                                                            const finalWidth = Math.max(barWidth, minWidth);

                                                            return (
                                                                <g key={i}>
                                                                    {/* NOMBRE DEL TIPO */}
                                                                    <text
                                                                        x="20"
                                                                        y={y + 38}
                                                                        style={{ fill: "#002a8d", fontSize: "21px", fontWeight: "700" }}
                                                                    >
                                                                        {tipo.tipo || 'Sin dato'}
                                                                    </text>

                                                                    {/* LÍNEA PUNTEADA */}
                                                                    <line 
                                                                        x1={labelWidth} 
                                                                        y1={y + 32} 
                                                                        x2={labelWidth + finalWidth} 
                                                                        y2={y + 32} 
                                                                        stroke="#ccc" 
                                                                        strokeWidth="1" 
                                                                        strokeDasharray="4,4" 
                                                                    />

                                                                    {/* BARRA AZUL */}
                                                                    <rect 
                                                                        x={labelWidth} 
                                                                        y={y + 12} 
                                                                        width={finalWidth} 
                                                                        height={48} 
                                                                        rx="7" 
                                                                        fill="#002a8d" 
                                                                    />

                                                                    {/* CANTIDAD */}
                                                                    <text
                                                                        x={labelWidth + 20}
                                                                        y={y + 42}
                                                                        style={{ fill: "white", fontSize: "24px", fontWeight: "800" }}
                                                                    >
                                                                        {tipo.cantidad}
                                                                    </text>

                                                                    {/* PORCENTAJE */}
                                                                    <text
                                                                        x={labelWidth + finalWidth + 15}
                                                                        y={y + 42}
                                                                        style={{ fill: "#002a8d", fontSize: "22px", fontWeight: "700" }}
                                                                    >
                                                                        {tipo.porcentaje}%
                                                                    </text>
                                                                </g>
                                                            );
                                                        })}
                                                    </svg>
                                                );
                                            })()
                                        ) : (
                                            <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                                                No hay datos disponibles
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* COLUMNA DERECHA */}
                            <div className="rt-grid-right">
                                <div className="rt-block">
                                    <h3 className="rt-block-title">Distribución por Departamento</h3>
                                    <div className="rt-chart-placeholder rt-chart-placeholder--tall">
                                        {datosDepartamento.length > 0 ? (
                                            (() => {
                                                const maxCount = Math.max(...datosDepartamento.map(d => d.cantidad));
                                                const maxSalary = Math.max(...datosDepartamento.map(d => d.salario));
                                                const labelWidth = 370;
                                                const countBarMaxWidth = 120;
                                                const salaryBarMaxWidth = 250;
                                                const totalWidth = labelWidth + countBarMaxWidth + salaryBarMaxWidth;
                                                const rowHeight = 35;
                                                
                                                return (
                                                    <svg width="100%" height={datosDepartamento.length * rowHeight + 10} viewBox={`0 0 ${totalWidth} ${datosDepartamento.length * rowHeight + 10}`} preserveAspectRatio="xMinYMin meet">
                                                        
                                                        {datosDepartamento.map((d, i) => {
                                                            const y = 5 + i * rowHeight;
                                                            
                                                            // Calcular anchos proporcionales
                                                            const countBarWidth = (d.cantidad / maxCount) * countBarMaxWidth;
                                                            const salaryBarWidth = (d.salario / maxSalary) * salaryBarMaxWidth;
                                                            
                                                            // Asegurar anchos mínimos
                                                            const minCountWidth = 50;
                                                            const minSalaryWidth = 70;
                                                            const finalCountWidth = Math.max(countBarWidth, minCountWidth);
                                                            const finalSalaryWidth = Math.max(salaryBarWidth, minSalaryWidth);
                                                            
                                                            const countBarX = labelWidth;
                                                            const salaryBarX = labelWidth + countBarMaxWidth + 10;

                                                            return (
                                                                <g key={i}>
                                                                    {/* NOMBRE DEL DEPARTAMENTO */}
                                                                    <text
                                                                        x="10"
                                                                        y={y + 20}
                                                                        style={{ fill: "#002a8d", fontSize: "16px", fontWeight: "600" }}
                                                                    >
                                                                        {d.departamento.length > 40 ? d.departamento.substring(0, 37) + '...' : d.departamento}
                                                                    </text>

                                                                    {/* BARRA DE CANTIDAD (naranja) */}
                                                                    <rect 
                                                                        x={countBarX} 
                                                                        y={y + 7} 
                                                                        width={finalCountWidth} 
                                                                        height={26} 
                                                                        rx="4" 
                                                                        fill="#f6a52d" 
                                                                    />

                                                                    {/* LABEL DE CANTIDAD */}
                                                                    <text
                                                                        x={countBarX + finalCountWidth / 2}
                                                                        y={y + 25}
                                                                        style={{ fill: "white", fontSize: "16px", fontWeight: "800", textAnchor: "middle" }}
                                                                    >
                                                                        {d.cantidad}
                                                                    </text>

                                                                    {/* BARRA DE SALARIO (azul) */}
                                                                    <rect
                                                                        x={salaryBarX}
                                                                        y={y + 7}
                                                                        width={finalSalaryWidth}
                                                                        height={26}
                                                                        rx="4"
                                                                        fill="#002a8d"
                                                                    />

                                                                    {/* LABEL DE SALARIO */}
                                                                    <text
                                                                        x={salaryBarX + finalSalaryWidth / 2}
                                                                        y={y + 25}
                                                                        style={{ fill: "white", fontSize: "15px", fontWeight: "800", textAnchor: "middle" }}
                                                                    >
                                                                        {formatMoneyCompact(d.salario, pais)}
                                                                    </text>
                                                                </g>
                                                            );
                                                        })}
                                                    </svg>
                                                );
                                            })()
                                        ) : (
                                            <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                                                No hay datos disponibles
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default RadarTalento;
