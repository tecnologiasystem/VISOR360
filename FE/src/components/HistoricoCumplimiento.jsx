// src/components/HistoricoCumplimiento.jsx

import React, { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";
import dayjs from "dayjs";
import "dayjs/locale/es";
dayjs.locale("es");
import { recaudoApi } from "../services/recaudoApiService";
import api from "../api";
import { useAuth } from "../contexts/AuthContext";
import "./HistoricoCumplimiento.css";

const PAISES = ["NPL COL", "ACC", "NPL PER", "NPL CHILE"];

// Función para obtener los últimos 3 meses dinámicamente
const getUltimos3Meses = () => {
  const now = dayjs();
  return [
    { 
      nombre: now.subtract(2, 'month').format('MMMM').charAt(0).toUpperCase() + now.subtract(2, 'month').format('MMMM').slice(1), 
      mes: now.subtract(2, 'month').month() + 1, 
      anio: now.subtract(2, 'month').year() 
    },
    { 
      nombre: now.subtract(1, 'month').format('MMMM').charAt(0).toUpperCase() + now.subtract(1, 'month').format('MMMM').slice(1), 
      mes: now.subtract(1, 'month').month() + 1, 
      anio: now.subtract(1, 'month').year() 
    },
    { 
      nombre: now.format('MMMM').charAt(0).toUpperCase() + now.format('MMMM').slice(1), 
      mes: now.month() + 1, 
      anio: now.year() 
    }
  ];
};

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        backgroundColor: 'white',
        border: '1px solid #ccc',
        padding: '12px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
      }}>
        <p style={{ margin: 0, fontWeight: 'bold', color: '#002F9E', marginBottom: '4px' }}>
          {label}
        </p>
        <p style={{ margin: 0, color: '#002F9E', fontSize: '18px', fontWeight: 'bold' }}>
          {payload[0].value}%
        </p>
        <p style={{ margin: 0, fontSize: '12px', color: '#666', marginTop: '4px' }}>
          Cumplimiento
        </p>
      </div>
    );
  }
  return null;
};

const HistoricoCumplimiento = () => {
  const { user } = useAuth();
  const campanasPermitidas = user?.campanas?.map(c => c.nombre) || [];
  
  const mesesConfig = getUltimos3Meses();
  const [data, setData] = useState(() => {
    const initial = {};
    mesesConfig.forEach(m => initial[m.nombre] = []);
    return initial;
  });

  useEffect(() => {
    const fetchData = async () => {
      const dataByMonth = {};

      try {
        const PAISES = ["NPL COL", "ACC", "NPL PER", "NPL CHILE"];
        
        // Para cada mes, obtener recaudo y meta de cada país
        for (const mesConfig of mesesConfig) {
          const paisesData = await Promise.all(
            PAISES.map(async (pais) => {
              try {
                // Obtener recaudo del país
                const responseRecaudo = await recaudoApi.get(`/recaudos/pais_by_name/${encodeURIComponent(pais)}`, {
                  params: { mes: mesConfig.mes, anio: mesConfig.anio, id_usuario: user?.id }
                });
                const totalRecaudo = responseRecaudo.data?.total_pais || 0;

                // Obtener meta del país
                const responseMeta = await recaudoApi.get(`/metas-campana/pais/${encodeURIComponent(pais)}`, {
                  params: { mes: mesConfig.mes, anio: mesConfig.anio }
                });
                const totalMeta = responseMeta.data?.meta_total || 0;

                // Calcular cumplimiento
                const cumplimiento = totalMeta > 0 ? Math.round((totalRecaudo / totalMeta) * 100) : 0;

                console.log(`📊 ${mesConfig.nombre} - ${pais}: Recaudo=${totalRecaudo}, Meta=${totalMeta}, Cumplimiento=${cumplimiento}%`);

                return {
                  name: pais.replace('NPL ', ''),
                  valor: cumplimiento
                };
              } catch (error) {
                console.error(`Error obteniendo datos de ${pais} para ${mesConfig.nombre}:`, error);
                return {
                  name: pais.replace('NPL ', ''),
                  valor: 0
                };
              }
            })
          );

          // Filtrar SOLO las campañas que están en user.campanas
          const paisesDataFiltrados = paisesData.filter(p => {
            // Reconstruir el nombre completo desde el nombre corto
            let nombreCompleto;
            if (p.name === 'COL') nombreCompleto = 'NPL COL';
            else if (p.name === 'PER') nombreCompleto = 'NPL PER';
            else if (p.name === 'CHILE') nombreCompleto = 'NPL CHILE';
            else if (p.name === 'ACC') nombreCompleto = 'ACC COL';
            else nombreCompleto = p.name;
            
            // Verificar si está en las campañas permitidas
            return campanasPermitidas.includes(nombreCompleto);
          });

          dataByMonth[mesConfig.nombre] = paisesDataFiltrados;
        }

        setData(dataByMonth);
        console.log('✅ Histórico de cumplimiento cargado:', dataByMonth);
      } catch (error) {
        console.error('Error cargando histórico de cumplimiento:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="historico-wrapper">
      <h3 className="hist-title">Histórico de cumplimiento</h3>

      {/* CONTENEDOR PRINCIPAL */}
      <div className="hist-container">

        {/* Tarjetas de meses */}
        {mesesConfig.map((mesConfig) => (
          <div key={mesConfig.nombre} className="hist-card">
            <h4 className="hist-mes">{mesConfig.nombre}</h4>

            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={data[mesConfig.nombre]} barCategoryGap="25%">
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis 
                  hide={false}
                  tick={{ fontSize: 11 }}
                  tickFormatter={(value) => `${value}%`}
                  domain={[0, 100]}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="valor" fill="#002F9E" radius={[4, 4, 0, 0]} maxBarSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ))}

      </div>
    </div>
  );
};

export default HistoricoCumplimiento;
