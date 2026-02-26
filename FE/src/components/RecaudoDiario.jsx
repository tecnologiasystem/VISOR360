// Componente para mostrar el scroll de recaudos diarios
import React, { useState, useEffect, useRef } from "react";
import { getRecaudoDiario, formatPeriodo, CAMPANA_MAP } from "../services/recaudoApiService";
import { Spin } from "antd";
import "./RecaudoDiario.css";

const fmt = (v) => {
  if (!v) return "$0";
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0
  }).format(v);
};

export default function RecaudoDiario({ idPais, nombreCampana, meses }) {
  const [recaudosDiarios, setRecaudosDiarios] = useState([]);
  const [loading, setLoading] = useState(false);
  const trackRef = useRef(null);

  useEffect(() => {
    const cargarRecaudosDiarios = async () => {
      if (!nombreCampana || !meses || meses.length === 0) return;
      
      setLoading(true);
      try {
        let todosLosRecaudos = [];
        let contadorDiaGlobal = 0;
        
        // Cargar datos de todos los meses seleccionados
        for (const mesData of meses) {
          const { mes, anio, label } = mesData;
          const periodo = formatPeriodo(mes, anio);
          
          // Usar el nuevo backend de recaudo
          const response = await getRecaudoDiario({ anioMes: periodo });
          
          // Filtrar por nombre de campaña
          const recaudosCampana = (response.data || []).filter(
            d => d.NombreCampana === nombreCampana
          );
          
          // Agrupar por día hábil, sumando todos los inversionistas
          const recaudosPorDia = {};
          recaudosCampana.forEach(r => {
            const dia = r.DiaHabil;
            if (!recaudosPorDia[dia]) {
              recaudosPorDia[dia] = 0;
            }
            recaudosPorDia[dia] += parseFloat(r.ValorRecaudoDia || 0);
          });
          
          // Convertir a array ordenado por día hábil
          const diasOrdenados = Object.keys(recaudosPorDia)
            .map(Number)
            .sort((a, b) => a - b);
          
          // Mapear a formato para mostrar
          const recaudosDelMes = diasOrdenados.map((diaHabil) => {
            contadorDiaGlobal++;
            // Calcular fecha aproximada (asumiendo días laborables)
            const fechaBase = new Date(anio, mes - 1, 1);
            let diasContados = 0;
            let fechaActual = new Date(fechaBase);
            while (diasContados < diaHabil) {
              const dow = fechaActual.getDay();
              if (dow !== 0 && dow !== 6) {
                diasContados++;
              }
              if (diasContados < diaHabil) {
                fechaActual.setDate(fechaActual.getDate() + 1);
              }
            }
            
            return {
              numeroDialaborable: contadorDiaGlobal,
              fecha: fechaActual.toISOString().split('T')[0],
              total: recaudosPorDia[diaHabil] || 0,
              mes: label,
              anio: anio,
              diaHabil: diaHabil
            };
          });
          
          todosLosRecaudos = [...todosLosRecaudos, ...recaudosDelMes];
        }
        
        setRecaudosDiarios(todosLosRecaudos);
      } catch (error) {
        console.error('Error al cargar recaudos diarios:', error);
        setRecaudosDiarios([]);
      } finally {
        setLoading(false);
      }
    };

    cargarRecaudosDiarios();
  }, [idPais, nombreCampana, meses]);

  // Scroll automático al día de hoy
  useEffect(() => {
    if (recaudosDiarios.length === 0 || !trackRef.current) return;
    
    const hoy = new Date().toISOString().split('T')[0];
    const indexHoy = recaudosDiarios.findIndex(d => d.fecha === hoy);
    
    if (indexHoy !== -1) {
      // Esperar a que el DOM se renderice
      setTimeout(() => {
        const cards = trackRef.current.querySelectorAll('.recaudo-dia-card');
        if (cards[indexHoy]) {
          cards[indexHoy].scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        }
      }, 100);
    }
  }, [recaudosDiarios]);

  const scroll = (direction) => {
    if (!trackRef.current) return;
    trackRef.current.scrollBy({
      left: direction === 'left' ? -300 : 300,
      behavior: 'smooth'
    });
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '20px' }}><Spin /></div>;
  }

  return (
    <div className="recaudo-diario-wrapper">
      <div className="recaudo-diario-track" ref={trackRef}>
        {recaudosDiarios.map((dia, index) => {
          const fecha = new Date(dia.fecha + 'T00:00:00');
          const diaNum = fecha.getDate();
          const mesNum = fecha.getMonth() + 1;
          
          // Verificar si es el primer día de un mes (excepto el primer día total)
          const esPrimerDiaDelMes = index > 0 && diaNum === 1;
          
          // Verificar si es hoy
          const hoy = new Date().toISOString().split('T')[0];
          const esHoy = dia.fecha === hoy;
          
          return (
            <React.Fragment key={index}>
              {esPrimerDiaDelMes && (
                <div style={{
                  width: '3px',
                  backgroundColor: '#003087',
                  margin: '0 8px',
                  borderRadius: '2px',
                  alignSelf: 'stretch',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  position: 'relative',
                  minHeight: '80px'
                }}>
                  <div style={{
                    position: 'absolute',
                    top: '-20px',
                    fontSize: '11px',
                    fontWeight: 600,
                    color: '#003087',
                    backgroundColor: 'white',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    whiteSpace: 'nowrap'
                  }}>
                    {dia.mes} {dia.anio}
                  </div>
                </div>
              )}
              <div 
                className="recaudo-dia-card"
                style={{
                  border: esHoy ? '3px solid #10b981' : undefined,
                  backgroundColor: esHoy ? '#ecfdf5' : undefined,
                  transform: esHoy ? 'scale(1.05)' : undefined,
                  boxShadow: esHoy ? '0 4px 12px rgba(16, 185, 129, 0.3)' : undefined
                }}
              >
                <div className="dia-monto">{fmt(dia.total)}</div>
                <div className="dia-label">
                  {esHoy && <span style={{ color: '#10b981', fontWeight: 700 }}>● </span>}
                  Día {dia.numeroDialaborable} · {diaNum.toString().padStart(2, '0')}/{mesNum.toString().padStart(2, '0')}
                </div>
              </div>
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
