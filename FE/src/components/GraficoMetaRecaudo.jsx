import React, { useState, useEffect } from 'react';
import { Spin } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine, Area, ComposedChart } from 'recharts';
import { recaudoApi } from '../services/recaudoApiService';
import './GraficoMetaRecaudo.css';

export default function GraficoMetaRecaudo({ idPais, mes, anio, metaTotal }) {
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState([]);
  const [diasLaborables, setDiasLaborables] = useState([]);
  const [ultimoDiaReal, setUltimoDiaReal] = useState(0);

  useEffect(() => {
    cargarDatos();
  }, [idPais, mes, anio, metaTotal]);

  const cargarDatos = async () => {
    setLoading(true);
    try {
      // Obtener días laborables del mes
      const respDias = await recaudoApi.get('/utils/dias-laborables', {
        params: { mes, anio }
      });
      
      // API devuelve { fechas: [...] }
      const dias = respDias.data.fechas || [];
      setDiasLaborables(dias);

      // Obtener recaudos diarios: soportar idNum o nombre de pais
      let recaudos = [];
      try {
        if (isNaN(Number(idPais))) {
          // idPais es un nombre (ej. 'NPL COL') -> usar endpoint por nombre
          const name = encodeURIComponent(idPais);
          const respRecaudos = await recaudoApi.get(`/recaudos/pais_by_name/${name}/diario`, { params: { mes, anio } });
          recaudos = respRecaudos.data || [];
        } else {
          const respRecaudos = await recaudoApi.get(`/recaudos/pais/${idPais}/diario`, { params: { mes, anio } });
          recaudos = respRecaudos.data || [];
        }
      } catch (err) {
        console.error('Error fetching recaudos diarios:', err);
        recaudos = [];
      }
      
      // Crear mapa de recaudos por fecha
      const recaudosPorFecha = {};
      recaudos.forEach(r => {
        const fecha = r.fecha.split('T')[0]; // YYYY-MM-DD
        recaudosPorFecha[fecha] = r.total;
      });

      // Calcular meta diaria (meta total / días laborables)
      const metaDiaria = dias.length > 0 ? metaTotal / dias.length : 0;

      // Construir datos para el gráfico
      let acumulado = 0;
      const data = dias.map((fechaStr, idx) => {
        const fecha = new Date(fechaStr);
        const fechaKey = fechaStr.split('T')[0];
        const recaudoDelDia = recaudosPorFecha[fechaKey] || 0;
        acumulado += recaudoDelDia;

        const diaNum = idx + 1;
        const metaAcumulada = metaDiaria * diaNum;

        return {
          dia: `Día ${diaNum}`,
          diaNum,
          fecha: `${fecha.getDate().toString().padStart(2, '0')}/${(fecha.getMonth() + 1).toString().padStart(2, '0')}`,
          recaudoAcumulado: acumulado,
          metaAcumulada,
          recaudoDelDia,
          metaDiaria
        };
      });

      // Obtener recaudo del mes anterior para comparación
      let recaudosMesAnterior = [];
      try {
        const mesAnt = mes === 1 ? 12 : mes - 1;
        const anioAnt = mes === 1 ? anio - 1 : anio;
        
        if (isNaN(Number(idPais))) {
          const name = encodeURIComponent(idPais);
          const respAnt = await recaudoApi.get(`/recaudos/pais_by_name/${name}/diario`, { 
            params: { mes: mesAnt, anio: anioAnt } 
          });
          recaudosMesAnterior = respAnt.data || [];
        } else {
          const respAnt = await recaudoApi.get(`/recaudos/pais/${idPais}/diario`, { 
            params: { mes: mesAnt, anio: anioAnt } 
          });
          recaudosMesAnterior = respAnt.data || [];
        }
      } catch (err) {
        console.error('Error fetching mes anterior:', err);
      }

      // Crear mapa acumulado del mes anterior por día laborable
      let acumAnt = 0;
      const recaudosAntPorDia = {};
      recaudosMesAnterior.forEach((r, idx) => {
        acumAnt += r.total;
        recaudosAntPorDia[idx + 1] = acumAnt;
      });

      // Actualizar data con comparación mes anterior
      data.forEach(d => {
        d.mesAnteriorAcum = recaudosAntPorDia[d.diaNum] || null;
      });

      // Calcular pronóstico con regresión lineal
      // Solo usar datos hasta hoy (donde hay recaudo real)
      const hoy = new Date();
      const datosReales = data.filter(d => {
        const [dia, mesNum] = d.fecha.split('/').map(Number);
        const fechaDato = new Date(anio, mesNum - 1, dia);
        return fechaDato <= hoy && d.recaudoAcumulado > 0;
      });

      let ultimoDiaRealNum = 0;
      
      if (datosReales.length >= 2) {
        // Regresión lineal: y = mx + b
        const n = datosReales.length;
        const sumX = datosReales.reduce((acc, d) => acc + d.diaNum, 0);
        const sumY = datosReales.reduce((acc, d) => acc + d.recaudoAcumulado, 0);
        const sumXY = datosReales.reduce((acc, d) => acc + d.diaNum * d.recaudoAcumulado, 0);
        const sumX2 = datosReales.reduce((acc, d) => acc + d.diaNum * d.diaNum, 0);

        const m = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
        const b = (sumY - m * sumX) / n;

        // Calcular error estándar para zona de confianza
        let sumErrores = 0;
        datosReales.forEach(d => {
          const predicho = m * d.diaNum + b;
          sumErrores += Math.pow(d.recaudoAcumulado - predicho, 2);
        });
        const errorEstandar = Math.sqrt(sumErrores / (n - 2));
        const margenConfianza = 1.96 * errorEstandar; // 95% confianza

        ultimoDiaRealNum = datosReales[datosReales.length - 1].diaNum;
        
        // Aplicar pronóstico a todos los días desde el último día real
        data.forEach(d => {
          if (d.diaNum > ultimoDiaRealNum) {
            const pred = m * d.diaNum + b;
            d.pronostico = pred;
            d.prediccionMin = pred - margenConfianza;
            d.prediccionMax = pred + margenConfianza;
          } else if (d.diaNum === ultimoDiaRealNum) {
            // Punto de conexión
            d.pronostico = d.recaudoAcumulado;
          }
        });
      }

      setUltimoDiaReal(ultimoDiaRealNum);
      setChartData(data);
    } catch (error) {
      console.error('Error al cargar datos del gráfico:', error);
      setChartData([]);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0
    }).format(value);
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const esPrediccion = data.diaNum > ultimoDiaReal;
      
      return (
        <div className="grafico-tooltip">
          <div className="tooltip-title">
            {data.dia} · {data.fecha}
            {esPrediccion && <span className="tooltip-badge">Proyección</span>}
          </div>
          
          <div className="tooltip-row">
            <span className="tooltip-label recaudo-label">💰 Recaudo Acum.:</span>
            <span className="tooltip-value">{formatCurrency(data.recaudoAcumulado)}</span>
          </div>
          
          <div className="tooltip-row">
            <span className="tooltip-label meta-label">🎯 Meta Acum.:</span>
            <span className="tooltip-value">{formatCurrency(data.metaAcumulada)}</span>
          </div>
          
          {data.mesAnteriorAcum && (
            <div className="tooltip-row">
              <span className="tooltip-label anterior-label">📅 Mes Anterior:</span>
              <span className="tooltip-value">{formatCurrency(data.mesAnteriorAcum)}</span>
            </div>
          )}
          
          {data.pronostico && esPrediccion && (
            <>
              <div className="tooltip-divider"></div>
              <div className="tooltip-row">
                <span className="tooltip-label pronostico-label">📈 Pronóstico:</span>
                <span className="tooltip-value">{formatCurrency(data.pronostico)}</span>
              </div>
              {data.prediccionMin && data.prediccionMax && (
                <div className="tooltip-row-small">
                  <span className="tooltip-label-small">Rango 95%:</span>
                  <span className="tooltip-value-small">
                    {formatCurrency(data.prediccionMin)} - {formatCurrency(data.prediccionMax)}
                  </span>
                </div>
              )}
            </>
          )}
          
          {!esPrediccion && (
            <>
              <div className="tooltip-divider"></div>
              <div className="tooltip-row">
                <span className="tooltip-label">Recaudo del día:</span>
                <span className="tooltip-value">{formatCurrency(data.recaudoDelDia)}</span>
              </div>
              <div className="tooltip-row">
                <span className="tooltip-label">Meta diaria:</span>
                <span className="tooltip-value">{formatCurrency(data.metaDiaria)}</span>
              </div>
            </>
          )}
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="grafico-meta-recaudo-loading">
        <Spin size="large" />
        <p>Cargando gráfico...</p>
      </div>
    );
  }

  if (chartData.length === 0) {
    return (
      <div className="grafico-meta-recaudo-empty">
        <p>No hay datos disponibles para mostrar el gráfico.</p>
      </div>
    );
  }

  return (
    <div className="grafico-meta-recaudo-container">
      <div className="grafico-header">
        <h3 className="grafico-title">Meta vs Recaudo Diario</h3>
        <p className="grafico-subtitle">Seguimiento día a día del cumplimiento de meta</p>
      </div>

      <ResponsiveContainer width="100%" height={450}>
        <ComposedChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
        >
          <defs>
            <linearGradient id="colorConfianza" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.2}/>
              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.05}/>
            </linearGradient>
          </defs>
          
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis 
            dataKey="dia" 
            tick={{ fontSize: 11, fill: '#666' }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis 
            tick={{ fontSize: 11, fill: '#666' }}
            tickFormatter={formatCurrency}
            width={100}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
          />
          
          {/* Zona de confianza de la predicción */}
          <Area
            type="monotone"
            dataKey="prediccionMax"
            stroke="none"
            fill="url(#colorConfianza)"
            fillOpacity={1}
            name="Zona Confianza"
            legendType="none"
          />
          <Area
            type="monotone"
            dataKey="prediccionMin"
            stroke="none"
            fill="white"
            fillOpacity={1}
            legendType="none"
          />
          
          {/* Línea de meta acumulada */}
          <Line 
            type="monotone" 
            dataKey="metaAcumulada" 
            stroke="#F59E0B" 
            strokeWidth={2.5}
            dot={false}
            activeDot={{ r: 5 }}
            name="🎯 Meta"
            strokeDasharray="6 3"
          />
          
          {/* Línea del mes anterior */}
          <Line 
            type="monotone" 
            dataKey="mesAnteriorAcum" 
            stroke="#94A3B8" 
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 5 }}
            name="📅 Mes Anterior"
            strokeDasharray="3 3"
            connectNulls
          />
          
          {/* Línea de recaudo real acumulado */}
          <Line 
            type="monotone" 
            dataKey="recaudoAcumulado" 
            stroke="#10B981" 
            strokeWidth={3}
            dot={{ r: 4, fill: '#10B981', strokeWidth: 2, stroke: '#fff' }}
            activeDot={{ r: 6 }}
            name="💰 Recaudo Real"
          />

          {/* Línea de pronóstico */}
          <Line 
            type="monotone" 
            dataKey="pronostico" 
            stroke="#3B82F6" 
            strokeWidth={2.5}
            strokeDasharray="8 4"
            dot={false}
            activeDot={{ r: 5 }}
            name="📈 Proyección"
            connectNulls
          />
          
          {/* Línea vertical en el último día real */}
          {ultimoDiaReal > 0 && (
            <ReferenceLine 
              x={`Día ${ultimoDiaReal}`} 
              stroke="#64748B" 
              strokeDasharray="3 3"
              label={{ value: 'Hoy', position: 'top', fill: '#64748B', fontSize: 11 }}
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
