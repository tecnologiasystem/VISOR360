import React, { useState, useEffect } from 'react';
import { Table, InputNumber, Button, message, Select, Card, Spin } from 'antd';
import { SaveOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import api from '../api';
import './GestionMetas.css';

const { Option } = Select;

const GestionMetas = () => {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [metas, setMetas] = useState([]);
  const [selectedPais, setSelectedPais] = useState('NPL COL');
  const [selectedMes, setSelectedMes] = useState(dayjs().month() + 1);
  const [selectedAnio, setSelectedAnio] = useState(dayjs().year());
  const [metasModificadas, setMetasModificadas] = useState({});

  const paises = ['NPL COL', 'ACC', 'NPL PER', 'NPL CHILE'];
  const meses = [
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
    { value: 12, label: 'Diciembre' }
  ];

  // Inversionistas por país (desde recaudo_mapping.json)
  const inversionistasPorPais = {
    'NPL COL': ['BANCOMEVA', 'IFC', 'PA', 'TUYA'],
    'ACC': ['BANCOLOMBIA'],
    'NPL PER': ['IFC', 'PROPIA'],
    'NPL CHILE': ['IFC']
  };

  useEffect(() => {
    cargarMetas();
  }, [selectedPais, selectedMes, selectedAnio]);

  const cargarMetas = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/metas-campana/pais/${selectedPais}`, {
        params: { mes: selectedMes, anio: selectedAnio }
      });

      const { metas_subcampanas, meta_total } = response.data;
      
      // Asegurar que todas las subcampañas del país tengan entrada
      const inversionistas = inversionistasPorPais[selectedPais] || [];
      const metasCompletas = inversionistas.map(inv => {
        const metaExistente = metas_subcampanas.find(m => m.nombre_campana === inv);
        return {
          nombre_campana: inv,
          meta_valor: metaExistente ? metaExistente.meta_valor : 0,
          id_meta: metaExistente?.id_meta || null
        };
      });

      setMetas(metasCompletas);
      setMetasModificadas({});
    } catch (error) {
      console.error('Error cargando metas:', error);
      // Si no hay metas, crear estructura vacía
      const inversionistas = inversionistasPorPais[selectedPais] || [];
      const metasVacias = inversionistas.map(inv => ({
        nombre_campana: inv,
        meta_valor: 0,
        id_meta: null
      }));
      setMetas(metasVacias);
    } finally {
      setLoading(false);
    }
  };

  const handleMetaChange = (nombreCampana, valor) => {
    setMetasModificadas({
      ...metasModificadas,
      [nombreCampana]: valor
    });
  };

  const guardarMetas = async () => {
    if (Object.keys(metasModificadas).length === 0) {
      message.warning('No hay cambios para guardar');
      return;
    }

    setSaving(true);
    try {
      const metasParaGuardar = Object.entries(metasModificadas).map(([nombre_campana, meta_valor]) => ({
        nombre_pais: selectedPais,
        nombre_campana,
        mes: selectedMes,
        anio: selectedAnio,
        meta_valor,
        usuario: 'admin' // TODO: obtener del contexto de autenticación
      }));

      await api.post('/metas-campana/bulk', metasParaGuardar);
      
      message.success('Metas guardadas correctamente');
      await cargarMetas(); // Recargar para actualizar IDs
    } catch (error) {
      console.error('Error guardando metas:', error);
      message.error('Error al guardar las metas');
    } finally {
      setSaving(false);
    }
  };

  const eliminarMeta = async (nombreCampana) => {
    try {
      await api.delete(`/metas-campana/pais/${selectedPais}/campana/${nombreCampana}`, {
        params: { mes: selectedMes, anio: selectedAnio }
      });
      
      message.success('Meta eliminada');
      await cargarMetas();
    } catch (error) {
      console.error('Error eliminando meta:', error);
      message.error('Error al eliminar la meta');
    }
  };

  const calcularTotal = () => {
    let total = 0;
    metas.forEach(meta => {
      const valorActual = metasModificadas[meta.nombre_campana] ?? meta.meta_valor;
      total += valorActual || 0;
    });
    return total;
  };

  const formatMoney = (value) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const columns = [
    {
      title: 'Subcampaña',
      dataIndex: 'nombre_campana',
      key: 'nombre_campana',
      width: 200
    },
    {
      title: 'Meta (COP)',
      dataIndex: 'meta_valor',
      key: 'meta_valor',
      width: 250,
      render: (valor, record) => {
        const valorActual = metasModificadas[record.nombre_campana] ?? valor;
        return (
          <InputNumber
            value={valorActual}
            onChange={(val) => handleMetaChange(record.nombre_campana, val)}
            formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
            parser={value => value.replace(/\$\s?|(,*)/g, '')}
            style={{ width: '100%' }}
            min={0}
          />
        );
      }
    },
    {
      title: 'Formato',
      key: 'formato',
      render: (_, record) => {
        const valorActual = metasModificadas[record.nombre_campana] ?? record.meta_valor;
        return formatMoney(valorActual || 0);
      }
    },
    {
      title: 'Acciones',
      key: 'acciones',
      width: 100,
      render: (_, record) => (
        record.id_meta && (
          <Button
            type="text"
            danger
            icon={<DeleteOutlined />}
            onClick={() => eliminarMeta(record.nombre_campana)}
          />
        )
      )
    }
  ];

  const metaTotal = calcularTotal();
  const hayModificaciones = Object.keys(metasModificadas).length > 0;

  return (
    <div className="gestion-metas-container">
      <Card
        title="Gestión de Metas por Subcampaña"
        extra={
          <div style={{ display: 'flex', gap: '10px' }}>
            <Button
              icon={<ReloadOutlined />}
              onClick={cargarMetas}
              loading={loading}
            >
              Recargar
            </Button>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={guardarMetas}
              loading={saving}
              disabled={!hayModificaciones}
            >
              Guardar Cambios
            </Button>
          </div>
        }
      >
        <div className="filtros-metas">
          <Select
            value={selectedPais}
            onChange={setSelectedPais}
            style={{ width: 150 }}
          >
            {paises.map(pais => (
              <Option key={pais} value={pais}>{pais}</Option>
            ))}
          </Select>

          <Select
            value={selectedMes}
            onChange={setSelectedMes}
            style={{ width: 150 }}
          >
            {meses.map(mes => (
              <Option key={mes.value} value={mes.value}>{mes.label}</Option>
            ))}
          </Select>

          <Select
            value={selectedAnio}
            onChange={setSelectedAnio}
            style={{ width: 100 }}
          >
            {[2024, 2025, 2026].map(anio => (
              <Option key={anio} value={anio}>{anio}</Option>
            ))}
          </Select>
        </div>

        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={metas}
            rowKey="nombre_campana"
            pagination={false}
            size="small"
            summary={() => (
              <Table.Summary fixed>
                <Table.Summary.Row style={{ backgroundColor: '#f0f0f0', fontWeight: 'bold' }}>
                  <Table.Summary.Cell index={0}>TOTAL</Table.Summary.Cell>
                  <Table.Summary.Cell index={1}>
                    {formatMoney(metaTotal)}
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={2} colSpan={2} />
                </Table.Summary.Row>
              </Table.Summary>
            )}
          />
        </Spin>

        {hayModificaciones && (
          <div style={{ marginTop: '10px', color: '#faad14' }}>
            Hay cambios sin guardar
          </div>
        )}
      </Card>
    </div>
  );
};

export default GestionMetas;
