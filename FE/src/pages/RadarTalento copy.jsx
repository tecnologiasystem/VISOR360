import React, { useState, useEffect, useMemo } from 'react';
import { Row, Col, Card, Select } from 'antd';
import {
    UserOutlined,
    DollarCircleOutlined,
    TeamOutlined,
    LineChartOutlined,
    FieldTimeOutlined,
} from '@ant-design/icons';
import { createPortal } from "react-dom";
import './RadarTalento.css';

const { Option } = Select;

const RadarTalento = () => {
    const [pais, setPais] = useState('País');
    const [mes, setMes] = useState('Mes');

    const resumenTop = [
        {
            key: 'personal',
            titulo: 'Personal Activo',
            valor: '301',
            icono: <UserOutlined />,
        },
        {
            key: 'costo',
            titulo: 'Costo recurso humano',
            valor: '$712.356.000',
            icono: <DollarCircleOutlined />,
        },
        {
            key: 'activas',
            titulo: 'Activas',
            valor: '209',
            icono: <TeamOutlined />,
            extra: '69%',
        },
        {
            key: 'activos',
            titulo: 'Activos',
            valor: '92',
            icono: <TeamOutlined />,
            extra: '31%',
        },
        {
            key: 'edad',
            titulo: 'Edad prom.',
            valor: '35',
            icono: <FieldTimeOutlined />,
        },
    ];

    const activosUnidad = [
        { key: 'acc', label: 'ACC', valor: '161', porcentaje: '53%' },
        { key: 'npl', label: 'NPL', valor: '44', porcentaje: '15%' },
        { key: 'staff', label: 'STAFF', valor: '76', porcentaje: '25%' },
        { key: 'otros', label: 'OTROS', valor: '76', porcentaje: '25%' },
    ];

    const barrasEjemplo = [
        { label: 'O. Labor', valor: 189, porcentaje: '63%' },
        { label: 'Indefinido', valor: 92, porcentaje: '31%' },
        { label: 'Aprendizaje', valor: 15, porcentaje: '15%' },
        { label: 'Fijo', valor: 5, porcentaje: '2%' },
    ];

    const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

    useEffect(() => {
        const onResize = () => setIsMobile(window.innerWidth <= 768);
        window.addEventListener("resize", onResize);
        return () => window.removeEventListener("resize", onResize);
    }, []);

    const mobilePortalRoot = useMemo(() => {
        let el = document.getElementById("rt-mobile-filters-root");
        if (!el) {
            el = document.createElement("div");
            el.id = "rt-mobile-filters-root";
            document.body.appendChild(el);
        }
        return el;
    }, []);


    return (
        <div className="radar-talento-page">   {/* ← Nuevo contenedor que controla el padding */}
            <div className="radar-talento-container">

                {/* === ENCABEZADO SUPERIOR === */}
                <div className="rt-header">
                    <h1 className="rt-title">Radar de Talento Humano</h1>

                    <div className="rt-filtros">
                        <Select
                            value={pais}
                            onChange={setPais}
                            className="rt-select"
                            getPopupContainer={() => document.body}
                            popupClassName="rt-select-popup"
                        >
                            <Option value="colombia">Colombia</Option>
                            <Option value="peru">Perú</Option>
                            <Option value="chile">Chile</Option>
                        </Select>

                        <Select
                            value={mes}
                            onChange={setMes}
                            className="rt-select"
                            getPopupContainer={() => document.body}
                            popupClassName="rt-select-popup"
                        >
                            <Option value="enero">Enero</Option>
                            <Option value="febrero">Febrero</Option>
                            <Option value="marzo">Marzo</Option>
                            <Option value="abril">Abril</Option>
                            <Option value="mayo">Mayo</Option>
                            <Option value="junio">Junio</Option>
                            <Option value="julio">Julio</Option>
                            <Option value="agosto">Agosto</Option>
                            <Option value="septiembre">Septiembre</Option>
                            <Option value="octubre">Octubre</Option>
                            <Option value="noviembre">Noviembre</Option>
                            <Option value="diciembre">Diciembre</Option>
                        </Select>

                    </div>
                </div>

                {/* ===== CONTENEDORES SUPERIORES AZULES ===== */}
                <div className="rt-summary">

                    {/* Grupo 1: Personal + Costo */}
                    <div className="rt-card group-large">

                        <div className="rt-item">
                            <span className="rt-title-small">{resumenTop[0].titulo}</span>
                            <div className="rt-value-row">
                                <span className="rt-icon">{resumenTop[0].icono}</span>
                                <span className="rt-value">{resumenTop[0].valor}</span>
                            </div>
                        </div>

                        <div className="rt-separator"></div>

                        <div className="rt-item">
                            <span className="rt-title-small">{resumenTop[1].titulo}</span>
                            <div className="rt-value-row">
                                <span className="rt-icon">{resumenTop[1].icono}</span>
                                <span className="rt-value">{resumenTop[1].valor}</span>
                            </div>
                        </div>

                    </div>


                    {/* Grupo 2: Activas + Activos */}
                    <div className="rt-card group-medium">

                        <div className="rt-item">
                            <span className="rt-title-small">{resumenTop[2].titulo}</span>
                            <div className="rt-value-row">
                                <span className="rt-icon">{resumenTop[2].icono}</span>
                                <span className="rt-value">{resumenTop[2].valor}</span>
                                <span className="rt-badge">{resumenTop[2].extra}</span>
                            </div>
                        </div>

                        <div className="rt-separator"></div>

                        <div className="rt-item">
                            <span className="rt-title-small">{resumenTop[3].titulo}</span>
                            <div className="rt-value-row">
                                <span className="rt-icon">{resumenTop[3].icono}</span>
                                <span className="rt-value">{resumenTop[3].valor}</span>
                                <span className="rt-badge">{resumenTop[3].extra}</span>
                            </div>
                        </div>

                    </div>


                    {/* Grupo 3: Edad */}
                    <div className="rt-card group-small">

                        <div className="rt-item">
                            <span className="rt-title-small">{resumenTop[4].titulo}</span>
                            <div className="rt-value-row">
                                <span className="rt-icon">{resumenTop[4].icono}</span>
                                <span className="rt-value">{resumenTop[4].valor}</span>
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

                    {/* COLUMNA IZQUIERDA (3 bloques) */}
                    <div className="rt-grid-left">

                        {/* Tipo de Contrato */}
                        {/* Tipo de Contrato */}
                        <div className="rt-block">
                            <h3 className="rt-block-title">Tipo de Contrato</h3>

                            <div className="rt-chart-area">

                                {(() => {
                                    // ==== DATOS (ficticios pero reales según tu maqueta) ====
                                    const contractData = [
                                        { label: "Obra o Labor", value: 189, pct: 63 },
                                        { label: "Indefinido", value: 92, pct: 31 },
                                        { label: "Aprendizaje", value: 15, pct: 15 },
                                        { label: "Fijo", value: 5, pct: 2 },
                                    ];

                                    const max = Math.max(...contractData.map(d => d.value));

                                    return (
                                        <svg viewBox="0 0 900 320" preserveAspectRatio="xMidYMid meet" className="rt-chart-svg">


                                            {(() => {
                                                const data = [
                                                    { label: "Obra o Labor", value: 189, pct: 63 },
                                                    { label: "Indefinido", value: 92, pct: 31 },
                                                    { label: "Aprendizaje", value: 15, pct: 15 },
                                                    { label: "Fijo", value: 5, pct: 2 },
                                                ];

                                                const max = Math.max(...data.map(d => d.value));

                                                // Aumentamos escala vertical (ANTES 150 → AHORA 200)
                                                const scale = 200;
                                                const baseY = 240; // bajamos el eje para dar más altura
                                                const sectionWidth = 900 / data.length;

                                                const linePoints = data.map((d, i) => {
                                                    const x = sectionWidth * i + sectionWidth / 2;
                                                    const y = baseY - (d.value / max) * scale;
                                                    return `${x},${y}`;
                                                }).join(" ");

                                                return (
                                                    <>
                                                        {/* Línea naranja */}
                                                        <polyline
                                                            fill="none"
                                                            stroke="#f6a52d"
                                                            strokeWidth="3"
                                                            points={linePoints}
                                                        />

                                                        {data.map((d, i) => {
                                                            const cx = sectionWidth * i + sectionWidth / 2;
                                                            const barHeight = (d.value / max) * scale;
                                                            const y = baseY - barHeight;

                                                            return (
                                                                <g key={i}>

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
                                                                        {d.pct}%
                                                                    </text>

                                                                    {/* Punto de línea */}
                                                                    <circle cx={cx} cy={y} r="4" fill="#ccc" />

                                                                    {/* Barra azul (más alta) */}
                                                                    <rect
                                                                        x={cx - 35}
                                                                        y={y}
                                                                        width="70"
                                                                        height={barHeight}
                                                                        fill="#002a8d"
                                                                        rx="5"
                                                                    />

                                                                    {/* Valor dentro de la barra */}
                                                                    <text
                                                                        x={cx}
                                                                        y={y + barHeight - 12}
                                                                        style={{
                                                                            fill: "white",
                                                                            fontSize: "26px",
                                                                            fontWeight: "800",
                                                                            textAnchor: "middle"
                                                                        }}
                                                                    >
                                                                        {d.value}
                                                                    </text>

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
                                                            );
                                                        })}
                                                    </>
                                                );
                                            })()}
                                        </svg>

                                    );
                                })()}

                            </div>
                        </div>


                        {/* Distribución por Cargo */}
                        <div className="rt-block">
                            <h3 className="rt-block-title">Distribución por Cargo</h3>
                            <div className="rt-chart-placeholder">
                                Gráfico de ejemplo (Distribución por Cargo)
                            </div>
                        </div>

                        {/* Tipo de Cargo */}
                        <div className="rt-block">
                            <h3 className="rt-block-title">Tipo de Cargo</h3>
                            <div className="rt-chart-placeholder">
                                Gráfico de ejemplo (Tipo de Cargo)
                            </div>
                        </div>

                    </div>

                    {/* COLUMNA DERECHA (1 bloque alto) */}
                    <div className="rt-grid-right">
                        {/* COLUMNA DERECHA (1 bloque alto) */}
                        <div className="rt-grid-right">
                            <div className="rt-block">
                                <h3 className="rt-block-title">Distribución por Departamento</h3>

                                {/* 🔥 IMPORTANTE: el SVG debe ir DENTRO de este div */}
                                <div className="rt-chart-placeholder rt-chart-placeholder--tall">

                                    {/* AQUÍ PEGAMOS EL SVG */}
                                    {(() => {
                                        const departamentos = [
                                            { label: "TOTAL GENERAL", count: 301, valor: "$712,36" },
                                            { label: "PRODUCTO ACC", count: 162, valor: "$274,81" },
                                            { label: "DIR. EJECUTIVA FINANCIERA Y RIESGO", count: 20, valor: "$86,53" },
                                            { label: "GER. GESTIÓN HUMANA FELICIDAD Y ADMIN.", count: 45, valor: "$85,26" },
                                            { label: "PRODUCTO NPL", count: 46, valor: "$78,09" },
                                            { label: "PRESIDENCIA", count: 2, valor: "$00,00" },
                                            { label: "GER. TECNOLOGÍA Y DESARROLLO", count: 14, valor: "$65,69" },
                                            { label: "GER. PLANEACIÓN DE NEGOCIO", count: 6, valor: "$28,60" },
                                            { label: "SECRETARÍA GENERAL", count: 5, valor: "$17,95" },
                                            { label: "GERENCIAL COMERCIAL", count: 1, valor: "$00,00" },
                                        ];

                                        const maxCount = Math.max(...departamentos.map(d => d.count));
                                        const barMaxWidth = 380; // un poco más pequeño para no romper bordes

                                        return (
                                            <svg width="100%" height={departamentos.length * 55}>
                                                {departamentos.map((d, i) => {
                                                    const y = i * 55 + 40;
                                                    const barWidth = (d.count / maxCount) * barMaxWidth;

                                                    return (
                                                        <g key={i}>
                                                            {/* LABEL */}
                                                            <text
                                                                x="10"
                                                                y={y - 14}
                                                                style={{ fill: "#002a8d", fontSize: "13px", fontWeight: "700" }}
                                                            >
                                                                {d.label}
                                                            </text>

                                                            {/* BARRA IZQUIERDA */}
                                                            <rect x="10" y={y} width={barWidth * 0.45} height="22" rx="3" fill="#f6a52d" />

                                                            {/* NÚMERO */}
                                                            <text
                                                                x={10 + barWidth * 0.45 - 10}
                                                                y={y + 16}
                                                                style={{ fill: "white", fontSize: "14px", fontWeight: "800", textAnchor: "end" }}
                                                            >
                                                                {d.count}
                                                            </text>

                                                            {/* BARRA DERECHA */}
                                                            <rect
                                                                x={10 + barWidth * 0.45}
                                                                y={y}
                                                                width={barWidth * 0.55}
                                                                height="22"
                                                                rx="3"
                                                                fill="#002a8d"
                                                            />

                                                            {/* VALOR ECONÓMICO */}
                                                            <text
                                                                x={10 + barWidth - 10}
                                                                y={y + 16}
                                                                style={{ fill: "white", fontSize: "14px", fontWeight: "800", textAnchor: "end" }}
                                                            >
                                                                {d.valor}
                                                            </text>
                                                        </g>
                                                    );
                                                })}
                                            </svg>
                                        );
                                    })()}

                                </div>
                            </div>
                        </div>

                    </div>

                </div>




            </div>
        </div>


    );




};

export default RadarTalento;
