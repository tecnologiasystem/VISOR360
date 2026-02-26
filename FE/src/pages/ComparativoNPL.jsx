import React, { useEffect, useState } from "react";
import {
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ComposedChart,
  ReferenceLine,
  CartesianGrid,
  Area
} from "recharts";
import dayjs from "dayjs";
import { getRecaudoComparativoDiaHabil } from "../services/recaudoApiService";
import apiMain from "../api";
import { useAuth } from "../contexts/AuthContext";

export default function ComparativoNPL({ nombreCampana }) {
  const { user } = useAuth();
  const [data, setData] = useState([]);
  const [ultimoDiaReal, setUltimoDiaReal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [insights, setInsights] = useState(null);

  const formatCurrency = (value) => {
    if (value == null) return '$0';
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatCurrencyShort = (value) => {
    if (value == null) return '$0';
    if (value >= 1000000000) return `$${(value / 1000000000).toFixed(1)}B`;
    if (value >= 1000000) return `$${(value / 1000000).toFixed(0)}M`;
    return `$${(value / 1000).toFixed(0)}K`;
  };

  useEffect(() => {
    const loadData = async () => {
      if (!nombreCampana) return;
      setLoading(true);
      setErrorMsg(null);

      try {
        const fechaActual = dayjs();
        const mesActual = fechaActual.month() + 1;
        const anioActual = fechaActual.year();
        const mesPasado = mesActual === 1 ? 12 : mesActual - 1;
        const anioPasado = mesActual === 1 ? anioActual - 1 : anioActual;

        // Inversionistas permitidos
        const inversionistasUsuario = user?.inversionistas?.map(inv =>
          inv.nombre_inversionista?.toUpperCase()
        ) || [];

        // Obtener Meta Actual
        let metaActual = 0;
        try {
          const respMeta = await apiMain.get(`/metas-campana/pais/${encodeURIComponent(nombreCampana)}`, {
            params: { mes: mesActual, anio: anioActual }
          });
          metaActual = respMeta.data?.meta_total || 0;
        } catch (e) { }

        // Obtener días laborables con fechas reales
        let diasLaborables = [];
        try {
          const respDias = await recaudoApi.get('/utils/dias-laborables', {
            params: { mes: mesActual, anio: anioActual }
          });
          diasLaborables = respDias.data.fechas || [];
        } catch (e) {
          console.warn('No se pudieron obtener días laborables');
        }

        // Normalizar nombre de campaña para el API
        // El backend espera "ACC" en lugar de "ACC COL"
        const mapaNombres = {
          'ACC COL': 'ACC',
          'ACC': 'ACC',
          'NPL COL': 'NPL COL',
          'NPL PER': 'NPL PER',
          'NPL CHILE': 'NPL CHILE'
        };
        const nombreCampanaApi = mapaNombres[nombreCampana] || nombreCampana;

        // Obtener datos comparativos
        const resp = await getRecaudoComparativoDiaHabil(
          nombreCampanaApi, mesActual, anioActual, mesPasado, anioPasado, null
        );

        const diaHabilActual = resp.dia_habil || 14;
        const datosActual = resp.mes_actual || {};
        const datosAnterior = resp.mes_comparar || {};
        const porCampanaActual = datosActual.por_campana || {};
        const porCampanaAnterior = datosAnterior.por_campana || {};
        const totalDiasActual = datosActual.total_dias_habiles_mes || 22;
        const totalDiasAnterior = datosAnterior.total_dias_habiles_mes || 22;

        // Filtrar por inversionistas permitidos
        const filtrarRecaudo = (porCampana) => {
          let total = 0;
          Object.entries(porCampana).forEach(([inv, valor]) => {
            const invUpper = inv.toUpperCase();
            const tieneAcceso = inversionistasUsuario.length === 0 ||
              inversionistasUsuario.includes(invUpper) ||
              inversionistasUsuario.some(i => invUpper.includes(i) || i.includes(invUpper));
            if (tieneAcceso) total += valor;
          });
          return total;
        };

        const recaudoActual = filtrarRecaudo(porCampanaActual);
        const recaudoAnteriorTotal = filtrarRecaudo(porCampanaAnterior);

        // Calcular recaudo comparable de diciembre AL MISMO DÍA HÁBIL
        // El gráfico distribuye el recaudo proporcionalmente, debemos hacer lo mismo para comparar
        const recaudoAnteriorAlDia = totalDiasAnterior > 0
          ? (recaudoAnteriorTotal / totalDiasAnterior) * diaHabilActual
          : 0;

        console.log('📊 DEBUG - Recaudo Actual (Ene):', formatCurrency(recaudoActual));
        console.log('📊 DEBUG - Recaudo Dic Total:', formatCurrency(recaudoAnteriorTotal));
        console.log('📊 DEBUG - Recaudo Dic al día ' + diaHabilActual + ':', formatCurrency(recaudoAnteriorAlDia));
        console.log('📊 DEBUG - Variación:', ((recaudoActual / recaudoAnteriorAlDia - 1) * 100).toFixed(1) + '%');

        // Calcular métricas
        const metaDiaria = totalDiasActual > 0 ? metaActual / totalDiasActual : 0;
        const metaAlDia = metaDiaria * diaHabilActual;
        const cumplimientoVsMeta = metaAlDia > 0 ? (recaudoActual / metaAlDia) : 1;

        // Usar recaudoAnteriorAlDia para comparación justa al mismo día hábil
        const cumplimientoVsAnterior = recaudoAnteriorAlDia > 0 ? (recaudoActual / recaudoAnteriorAlDia) : 1;

        // Proyección de cierre (basada en ritmo actual)
        const ritmoActual = diaHabilActual > 0 ? recaudoActual / diaHabilActual : 0;
        const proyeccionCierre = ritmoActual * totalDiasActual;
        const brechaVsMeta = metaActual - proyeccionCierre;

        // Guardar insights
        setInsights({
          recaudoActual,
          recaudoAnterior: recaudoAnteriorAlDia,  // Usar el valor comparable
          recaudoAnteriorTotal,
          metaActual,
          metaAlDia,
          diaHabil: diaHabilActual,
          totalDias: totalDiasActual,
          cumplimientoVsMeta,
          cumplimientoVsAnterior,
          proyeccionCierre,
          brechaVsMeta,
          adelanteVsMeta: recaudoActual >= metaAlDia,
          adelanteVsAnterior: recaudoActual >= recaudoAnteriorAlDia
        });

        // Construir datos del gráfico
        const maxDias = Math.max(totalDiasActual, totalDiasAnterior);
        const recaudoDiarioActual = diaHabilActual > 0 ? recaudoActual / diaHabilActual : 0;
        const recaudoDiarioAnterior = totalDiasAnterior > 0 ? recaudoAnteriorTotal / (resp.dia_habil || diaHabilActual) : 0;

        const chartData = [];
        let acumActual = 0;
        let acumAnterior = 0;

        for (let dia = 1; dia <= maxDias; dia++) {
          const esFuturo = dia > diaHabilActual;

          // Obtener fecha real del día hábil
          const fechaReal = diasLaborables[dia - 1]
            ? dayjs(diasLaborables[dia - 1]).format('DD MMM')
            : '';

          // Mes actual
          if (!esFuturo) {
            acumActual += recaudoDiarioActual;
          }

          // Mes anterior (simulado proporcionalmente)
          if (dia <= totalDiasAnterior) {
            acumAnterior = (recaudoAnteriorTotal / totalDiasAnterior) * dia;
          }

          const punto = {
            dia: fechaReal ? `Día ${dia} (${fechaReal})` : `Día ${dia}`,
            diaNum: dia,
            metaAcumulada: metaDiaria * dia,
            mesAnterior: dia <= totalDiasAnterior ? acumAnterior : null,
            recaudoAcumulado: esFuturo ? null : acumActual,
            esFuturo
          };

          // Proyección para días futuros (solo agregar si es futuro o es el día actual)
          if (esFuturo) {
            punto.proyeccion = acumActual + (ritmoActual * (dia - diaHabilActual));
          } else if (dia === diaHabilActual) {
            punto.proyeccion = acumActual;
          }

          chartData.push(punto);
        }

        setUltimoDiaReal(diaHabilActual);
        setData(chartData);

      } catch (err) {
        console.error("Error:", err);
        setErrorMsg("Error cargando datos");
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [nombreCampana, user]);

  if (loading) return <div style={{ textAlign: 'center', padding: '40px' }}>Cargando...</div>;
  if (errorMsg) return <div style={{ textAlign: 'center', padding: '40px', color: '#EF4444' }}>{errorMsg}</div>;
  if (!insights) return null;

  const mesActualNombre = dayjs().format('MMM YYYY');
  const mesPasadoNombre = dayjs().subtract(1, 'month').format('MMM YYYY');

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '20px' }}>
      {/* Header con título */}
      <div style={{ textAlign: 'center', marginBottom: '15px' }}>
        <h2 style={{ color: '#003087', margin: 0, fontSize: '20px' }}>
          Análisis Comparativo - {nombreCampana}
        </h2>
        <p style={{ color: '#666', fontSize: '12px', margin: '5px 0' }}>
          Día hábil {insights.diaHabil} de {insights.totalDias} | {mesActualNombre} vs {mesPasadoNombre}
        </p>
      </div>

      {/* Cards de métricas */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '12px',
        marginBottom: '20px'
      }}>
        {/* Recaudo Actual */}
        <div style={{
          background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
          borderRadius: '12px',
          padding: '15px',
          color: 'white'
        }}>
          <div style={{ fontSize: '11px', opacity: 0.9 }}>Recaudo Actual</div>
          <div style={{ fontSize: '20px', fontWeight: 'bold' }}>{formatCurrencyShort(insights.recaudoActual)}</div>
          <div style={{ fontSize: '11px', marginTop: '5px' }}>
            {insights.adelanteVsAnterior ? '↑' : '↓'} {((insights.cumplimientoVsAnterior - 1) * 100).toFixed(0)}% vs {mesPasadoNombre}
          </div>
        </div>

        {/* Meta Esperada al día */}
        <div style={{
          background: insights.adelanteVsMeta ? 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)' : 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
          borderRadius: '12px',
          padding: '15px',
          color: 'white'
        }}>
          <div style={{ fontSize: '11px', opacity: 0.9 }}>Meta al Día {insights.diaHabil}</div>
          <div style={{ fontSize: '20px', fontWeight: 'bold' }}>{formatCurrencyShort(insights.metaAlDia)}</div>
          <div style={{ fontSize: '11px', marginTop: '5px' }}>
            {insights.adelanteVsMeta ? '✓ Adelante' : '⚠ Atrás'} {((insights.cumplimientoVsMeta - 1) * 100).toFixed(0)}%
          </div>
        </div>

        {/* Proyección de Cierre */}
        <div style={{
          background: insights.proyeccionCierre >= insights.metaActual
            ? 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)'
            : 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)',
          borderRadius: '12px',
          padding: '15px',
          color: 'white'
        }}>
          <div style={{ fontSize: '11px', opacity: 0.9 }}>Proyección Cierre</div>
          <div style={{ fontSize: '20px', fontWeight: 'bold' }}>{formatCurrencyShort(insights.proyeccionCierre)}</div>
          <div style={{ fontSize: '11px', marginTop: '5px' }}>
            {insights.proyeccionCierre >= insights.metaActual ? '✓ Cumple meta' : `Falta ${formatCurrencyShort(Math.abs(insights.brechaVsMeta))}`}
          </div>
        </div>

        {/* Meta Total */}
        <div style={{
          background: 'linear-gradient(135deg, #6B7280 0%, #4B5563 100%)',
          borderRadius: '12px',
          padding: '15px',
          color: 'white'
        }}>
          <div style={{ fontSize: '11px', opacity: 0.9 }}>Meta del Mes</div>
          <div style={{ fontSize: '20px', fontWeight: 'bold' }}>{formatCurrencyShort(insights.metaActual)}</div>
          <div style={{ fontSize: '11px', marginTop: '5px' }}>
            {((insights.recaudoActual / insights.metaActual) * 100).toFixed(0)}% completado
          </div>
        </div>
      </div>

      {/* Gráfico */}
      <div style={{ background: '#fff', borderRadius: '12px', padding: '20px', boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
        <ResponsiveContainer width="100%" height={350}>
          <ComposedChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
            <defs>
              <linearGradient id="gradProyeccion" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="dia" angle={-45} textAnchor="end" height={60} tick={{ fontSize: 9 }} interval={1} />
            <YAxis tickFormatter={(v) => `$${(v / 1000000).toFixed(0)}M`} width={60} tick={{ fontSize: 10 }} />
            <Tooltip formatter={(v) => formatCurrency(v)} contentStyle={{ borderRadius: '8px' }} />
            <Legend verticalAlign="top" height={36} />

            {/* Mes anterior */}
            <Line
              type="monotone"
              dataKey="mesAnterior"
              name={`${mesPasadoNombre}`}
              stroke="#9CA3AF"
              strokeWidth={2}
              strokeDasharray="4 4"
              dot={false}
            />

            {/* Meta */}
            <Line
              type="monotone"
              dataKey="metaAcumulada"
              name="Meta"
              stroke="#F59E0B"
              strokeWidth={2}
              dot={false}
              strokeDasharray="6 3"
            />

            {/* Recaudo Real */}
            <Line
              type="monotone"
              dataKey="recaudoAcumulado"
              name="Recaudo Real"
              stroke="#10B981"
              strokeWidth={3}
              dot={{ r: 3, fill: '#10B981' }}
              activeDot={{ r: 6 }}
            />

            {/* Proyección */}
            <Line
              type="monotone"
              dataKey="proyeccion"
              name="Proyección"
              stroke="#8B5CF6"
              strokeWidth={2}
              strokeDasharray="4 4"
              dot={false}
              connectNulls
            />

            {ultimoDiaReal > 0 && (
              <ReferenceLine x={`Día ${ultimoDiaReal}`} stroke="#EF4444" strokeWidth={2} strokeDasharray="3 3" label={{ value: 'Hoy', fill: '#EF4444', fontSize: 11 }} />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
