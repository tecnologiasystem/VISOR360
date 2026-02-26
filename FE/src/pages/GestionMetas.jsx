import React, { useState, useEffect, useCallback } from 'react';
import { Table, InputNumber, Button, message, Select, Card, Spin, Tag, Tooltip, Space, Typography, Modal } from 'antd';
import { SaveOutlined, DeleteOutlined, ReloadOutlined, InfoCircleOutlined, UserOutlined, ClockCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { useLocation, useNavigate, UNSAFE_NavigationContext } from 'react-router-dom';
import dayjs from 'dayjs';
import { useAuth } from '../contexts/AuthContext';
import api from '../api';
import './GestionMetas.css';

const { Option } = Select;
const { Title, Text } = Typography;

const GestionMetas = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [metas, setMetas] = useState([]);
  const [selectedPais, setSelectedPais] = useState(null);
  const [selectedMes, setSelectedMes] = useState(dayjs().month() + 1);
  const [selectedAnio, setSelectedAnio] = useState(dayjs().year());
  const [metasModificadas, setMetasModificadas] = useState({});
  const [recaudosModificados, setRecaudosModificados] = useState({});
  const [confirmedNavigation, setConfirmedNavigation] = useState(false);
  const [lastLocation, setLastLocation] = useState(null);

  // Filtrar países/campañas según permisos del usuario
  const todasLasCampanas = ['NPL COL', 'ACC', 'NPL PER', 'NPL CHILE'];

  // Mapeo de nombre de campaña del usuario a nombre de "país" en el sistema
  const mapeoNombreCampana = {
    'ACC COL': 'ACC',
    'ACC': 'ACC',
    'NPL COL': 'NPL COL',
    'NPL PER': 'NPL PER',
    'NPL PERU': 'NPL PER',
    'NPL CHILE': 'NPL CHILE'
  };

  // Obtener campañas del usuario y filtrar
  const campanasUsuario = user?.campanas?.map(c => mapeoNombreCampana[c.nombre] || c.nombre) || [];
  const paises = todasLasCampanas.filter(pais => campanasUsuario.includes(pais));

  // Formateo de moneda según país
  const formatMoney = (value, pais) => {
    if (value === null || value === undefined) return '$0';

    const numero = Number(value);
    if (isNaN(numero)) return '$0';

    // Determinar símbolo y locale según país
    let simbolo = '$';
    let locale = 'es-CO';

    if (pais?.includes('PER')) {
      simbolo = 'S/';
      locale = 'es-PE';
    } else if (pais?.includes('CHILE')) {
      simbolo = '$';
      locale = 'es-CL';
    } else {
      // Colombia por defecto
      simbolo = '$';
      locale = 'es-CO';
    }

    return simbolo + ' ' + numero.toLocaleString(locale, {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  };

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

  // Inversionistas por país (mapa completo del sistema)
  const inversionistasPorPaisSistema = {
    'NPL COL': ['BANCOOMEVA', 'IFC', 'PA', 'TUYA'],
    'ACC': ['ACCION', 'ADAMANTINE', 'CREDIVALORES', 'INTERASEO', 'JCAP', 'PRA', 'PRAGROUP'],
    'NPL PER': ['IFC', 'PROPIA'],
    'NPL CHILE': ['IFC']
  };

  // Obtener nombres de inversionistas asignados al usuario
  const inversionistasUsuario = user?.inversionistas?.map(inv => inv.nombre_inversionista?.toUpperCase()) || [];

  // Filtrar inversionistas por país según lo que el usuario tiene asignado
  const inversionistasPorPais = {};
  Object.keys(inversionistasPorPaisSistema).forEach(pais => {
    const inversionistasDelPais = inversionistasPorPaisSistema[pais];
    // Filtrar solo los inversionistas que el usuario tiene asignados
    const inversionistasFiltrados = inversionistasDelPais.filter(inv =>
      inversionistasUsuario.includes(inv.toUpperCase()) || inversionistasUsuario.includes(inv.replace('GROUP', '').toUpperCase())
    );
    inversionistasPorPais[pais] = inversionistasFiltrados.length > 0 ? inversionistasFiltrados : [];
  });

  // Establecer la primera campaña disponible cuando se cargan los paises
  useEffect(() => {
    if (!selectedPais && paises.length > 0) {
      setSelectedPais(paises[0]);
    }
  }, [paises, selectedPais]);

  useEffect(() => {
    if (selectedPais) {
      cargarMetas();
    }
  }, [selectedPais, selectedMes, selectedAnio]);

  // Bloquear navegación si hay cambios sin guardar (compatible con BrowserRouter)
  const { navigator } = React.useContext(UNSAFE_NavigationContext);

  useEffect(() => {
    if (!navigator) return;

    const { push } = navigator;

    navigator.push = (...args) => {
      const hayModificaciones = Object.keys(metasModificadas).length > 0 || Object.keys(recaudosModificados).length > 0;

      if (hayModificaciones && !confirmedNavigation) {
        const totalCambios = Object.keys(metasModificadas).length + Object.keys(recaudosModificados).length;

        Modal.confirm({
          title: 'Cambios sin guardar',
          icon: <ExclamationCircleOutlined style={{ color: '#faad14' }} />,
          content: `Tienes ${totalCambios} cambio(s) sin guardar. ¿Deseas descartarlos y salir?`,
          okText: 'Descartar y salir',
          okType: 'danger',
          cancelText: 'Continuar editando',
          onOk() {
            setConfirmedNavigation(true);
            setLastLocation(args[0]);
          }
        });
      } else {
        push(...args);
      }
    };

    return () => {
      navigator.push = push;
    };
  }, [navigator, metasModificadas, recaudosModificados, confirmedNavigation]);

  // Ejecutar navegación confirmada
  useEffect(() => {
    if (confirmedNavigation && lastLocation) {
      navigate(lastLocation);
      setConfirmedNavigation(false);
      setLastLocation(null);
    }
  }, [confirmedNavigation, lastLocation, navigate]);

  // Prevenir salida del navegador si hay cambios sin guardar
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      const hayModificaciones = Object.keys(metasModificadas).length > 0 || Object.keys(recaudosModificados).length > 0;
      if (hayModificaciones) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [metasModificadas, recaudosModificados]);

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
          id_meta: metaExistente?.id_meta || null,
          usuario_modificacion: metaExistente?.usuario_modificacion || null,
          fecha_modificacion: metaExistente?.fecha_modificacion || null,
          usuario_creacion: metaExistente?.usuario_creacion || null,
          fecha_creacion: metaExistente?.fecha_creacion || null,
          recaudo_manual: metaExistente?.recaudo_manual || 0
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
      [nombreCampana]: valor ?? 0
    });
  };

  const handleRecaudoManualChange = (nombreCampana, valor) => {
    setRecaudosModificados({
      ...recaudosModificados,
      [nombreCampana]: valor ?? 0
    });
  };

  const guardarMetas = async () => {
    const hayModificacionesMeta = Object.keys(metasModificadas).length > 0;
    const hayModificacionesRecaudo = Object.keys(recaudosModificados).length > 0;

    if (!hayModificacionesMeta && !hayModificacionesRecaudo) {
      message.warning('No hay cambios para guardar');
      return;
    }

    setSaving(true);
    try {
      // Combinar cambios de metas y recaudos manuales
      const todasLasCampanas = new Set([
        ...Object.keys(metasModificadas),
        ...Object.keys(recaudosModificados)
      ]);

      const metasParaGuardar = Array.from(todasLasCampanas).map(nombre_campana => {
        const metaActual = metas.find(m => m.nombre_campana === nombre_campana);
        return {
          nombre_pais: selectedPais,
          nombre_campana,
          mes: selectedMes,
          anio: selectedAnio,
          meta_valor: metasModificadas[nombre_campana] ?? metaActual?.meta_valor ?? 0,
          recaudo_manual: recaudosModificados[nombre_campana] ?? metaActual?.recaudo_manual ?? 0,
          usuario: user?.username || user?.nombre || 'sistema'
        };
      });

      await api.post('/metas-campana/bulk', metasParaGuardar);

      // Limpiar estados de modificaciones
      setMetasModificadas({});
      setRecaudosModificados({});

      // Recargar metas para obtener el total actualizado
      await cargarMetas(); // Recargar para actualizar IDs

      // Obtener meta_total actualizado desde el backend
      try {
        const respMeta = await api.get(`/metas-campana/pais/${selectedPais}`, {
          params: { mes: selectedMes, anio: selectedAnio }
        });
        const meta_total = respMeta.data?.meta_total || 0;

        // Disparar evento para actualizar otros componentes (incluye meta_total)
        window.dispatchEvent(new CustomEvent('metasActualizadas', {
          detail: { pais: selectedPais, mes: selectedMes, anio: selectedAnio, meta_total }
        }));
      } catch (e) {
        // Si falla, enviar evento sin meta_total
        window.dispatchEvent(new CustomEvent('metasActualizadas', {
          detail: { pais: selectedPais, mes: selectedMes, anio: selectedAnio }
        }));
      }

      message.success('Metas guardadas correctamente');
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

      // Recargar metas para obtener el total actualizado
      await cargarMetas();
      try {
        const respMeta = await api.get(`/metas-campana/pais/${selectedPais}`, {
          params: { mes: selectedMes, anio: selectedAnio }
        });
        const meta_total = respMeta.data?.meta_total || 0;
        window.dispatchEvent(new CustomEvent('metasActualizadas', {
          detail: { pais: selectedPais, mes: selectedMes, anio: selectedAnio, meta_total }
        }));
      } catch (e) {
        window.dispatchEvent(new CustomEvent('metasActualizadas', {
          detail: { pais: selectedPais, mes: selectedMes, anio: selectedAnio }
        }));
      }

      message.success('Meta eliminada');
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

  const columns = [
    {
      title: 'Subcampaña',
      dataIndex: 'nombre_campana',
      key: 'nombre_campana',
      width: 180,
      render: (text, record) => (
        <Space direction="vertical" size={0}>
          <Text strong style={{ color: '#002a8d' }}>{text}</Text>
          {record.id_meta && (
            <Text type="secondary" style={{ fontSize: '11px' }}>
              ID: {record.id_meta}
            </Text>
          )}
        </Space>
      )
    },
    {
      title: `Meta (${selectedPais?.includes('PER') ? 'PEN' : selectedPais?.includes('CHILE') ? 'CLP' : 'COP'})`,
      dataIndex: 'meta_valor',
      key: 'meta_valor',
      width: 220,
      render: (valor, record) => {
        const valorActual = record.nombre_campana in metasModificadas ? metasModificadas[record.nombre_campana] : valor;
        const modificado = record.nombre_campana in metasModificadas;

        // Determinar símbolo según país
        const simbolo = selectedPais?.includes('PER') ? 'S/' : '$';

        return (
          <div style={{ position: 'relative' }}>
            <InputNumber
              value={valorActual}
              onChange={(val) => handleMetaChange(record.nombre_campana, val)}
              formatter={value => `${simbolo} ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={value => value.replace(/S\/\s?|\$\s?|(,*)/g, '')}
              style={{
                width: '100%',
                borderColor: modificado ? '#faad14' : undefined,
                boxShadow: modificado ? '0 0 0 2px rgba(250, 173, 20, 0.2)' : undefined
              }}
              min={0}
            />
            {modificado && (
              <Tag color="orange" style={{ position: 'absolute', top: -8, right: -8, fontSize: '10px' }}>
                Editado
              </Tag>
            )}
          </div>
        );
      }
    },
    {
      title: 'Formato',
      key: 'formato',
      width: 150,
      render: (_, record) => {
        const valorActual = record.nombre_campana in metasModificadas ? metasModificadas[record.nombre_campana] : record.meta_valor;
        return (
          <Tag color="blue" style={{ fontSize: '13px', padding: '4px 12px' }}>
            {formatMoney(valorActual || 0, selectedPais)}
          </Tag>
        );
      }
    },
    {
      title: (
        <Tooltip title="Recaudo manual para subcampañas sin data en BD (ej: Interaseo)">
          <Space>
            Recaudo Manual
            <InfoCircleOutlined style={{ color: '#1890ff' }} />
          </Space>
        </Tooltip>
      ),
      key: 'recaudo_manual',
      width: 220,
      render: (_, record) => {
        const valorActual = record.nombre_campana in recaudosModificados ? recaudosModificados[record.nombre_campana] : record.recaudo_manual;
        const modificado = record.nombre_campana in recaudosModificados;
        const esInteraseo = record.nombre_campana.toUpperCase() === 'INTERASEO';

        // Determinar símbolo según país
        const simbolo = selectedPais?.includes('PER') ? 'S/' : '$';

        // Si NO es Interaseo, mostrar solo el valor sin permitir edición
        if (!esInteraseo) {
          return (
            <Text type="secondary" style={{ fontSize: '13px' }}>
              N/A
            </Text>
          );
        }

        return (
          <div style={{ position: 'relative' }}>
            <InputNumber
              value={valorActual}
              onChange={(val) => handleRecaudoManualChange(record.nombre_campana, val)}
              formatter={value => `${simbolo} ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={value => value.replace(/S\/\s?|\$\s?|(,*)/g, '')}
              style={{
                width: '100%',
                borderColor: modificado ? '#52c41a' : undefined,
                boxShadow: modificado ? '0 0 0 2px rgba(82, 196, 26, 0.2)' : undefined
              }}
              min={0}
              placeholder="0"
            />
            {modificado && (
              <Tag color="green" style={{ position: 'absolute', top: -8, right: -8, fontSize: '10px' }}>
                Editado
              </Tag>
            )}
          </div>
        );
      }
    },
    {
      title: (
        <Space>
          <InfoCircleOutlined />
          Auditoría
        </Space>
      ),
      key: 'auditoria',
      width: 200,
      render: (_, record) => {
        if (!record.id_meta) {
          return <Text type="secondary" style={{ fontSize: '12px' }}>Sin registrar</Text>;
        }

        const usuarioMod = record.usuario_modificacion || record.usuario_creacion;
        const fechaMod = record.fecha_modificacion || record.fecha_creacion;

        return (
          <Tooltip
            title={
              <div style={{ padding: '8px' }}>
                <div style={{ marginBottom: '8px' }}>
                  <strong>Creado por:</strong> {record.usuario_creacion || 'N/A'}<br />
                  <strong>Fecha:</strong> {record.fecha_creacion ? dayjs(record.fecha_creacion).format('DD/MM/YYYY HH:mm') : 'N/A'}
                </div>
                {record.fecha_modificacion && (
                  <div>
                    <strong>Última modificación:</strong> {record.usuario_modificacion || 'N/A'}<br />
                    <strong>Fecha:</strong> {dayjs(record.fecha_modificacion).format('DD/MM/YYYY HH:mm')}
                  </div>
                )}
              </div>
            }
            placement="left"
          >
            <Space direction="vertical" size={0} style={{ cursor: 'pointer' }}>
              <Space size={4}>
                <UserOutlined style={{ fontSize: '11px', color: '#1890ff' }} />
                <Text style={{ fontSize: '12px' }}>{usuarioMod || 'N/A'}</Text>
              </Space>
              <Space size={4}>
                <ClockCircleOutlined style={{ fontSize: '11px', color: '#52c41a' }} />
                <Text type="secondary" style={{ fontSize: '11px' }}>
                  {fechaMod ? dayjs(fechaMod).format('DD/MM/YY HH:mm') : 'N/A'}
                </Text>
              </Space>
            </Space>
          </Tooltip>
        );
      }
    },
    {
      title: 'Acciones',
      key: 'acciones',
      width: 80,
      align: 'center',
      render: (_, record) => (
        record.id_meta && (
          <Tooltip title="Eliminar meta">
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              onClick={() => eliminarMeta(record.nombre_campana)}
              size="small"
            />
          </Tooltip>
        )
      )
    }
  ];

  const metaTotal = calcularTotal();
  const hayModificaciones = Object.keys(metasModificadas).length > 0 || Object.keys(recaudosModificados).length > 0;
  const totalCambios = Object.keys(metasModificadas).length + Object.keys(recaudosModificados).length;

  return (
    <div className="gestion-metas-container">
      <div style={{ marginBottom: '20px' }}>
        <Title level={2} style={{ margin: 0, color: '#002a8d' }}>
          Gestión de Metas por Subcampaña
        </Title>
        <Text type="secondary">
          Configure y administre las metas mensuales por inversionista
        </Text>
      </div>

      {hayModificaciones && (
        <div style={{
          marginBottom: '16px',
          padding: '12px 16px',
          background: '#fffbe6',
          border: '1px solid #ffe58f',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <InfoCircleOutlined style={{ color: '#faad14', fontSize: '16px' }} />
          <Text style={{ color: '#ad8b00' }}>
            Hay <strong>{totalCambios}</strong> cambio(s) sin guardar
          </Text>
        </div>
      )}

      <Card
        className="metas-card"
        bordered={false}
        style={{
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: '12px'
        }}
      >
        <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <Space size="middle" wrap>
            <div>
              <Text type="secondary" style={{ display: 'block', marginBottom: '4px', fontSize: '12px' }}>País</Text>
              <Select
                value={selectedPais}
                onChange={setSelectedPais}
                style={{ width: 150 }}
                size="large"
              >
                {paises.map(pais => (
                  <Option key={pais} value={pais}>{pais}</Option>
                ))}
              </Select>
            </div>

            <div>
              <Text type="secondary" style={{ display: 'block', marginBottom: '4px', fontSize: '12px' }}>Mes</Text>
              <Select
                value={selectedMes}
                onChange={setSelectedMes}
                style={{ width: 150 }}
                size="large"
              >
                {meses.map(mes => (
                  <Option key={mes.value} value={mes.value}>{mes.label}</Option>
                ))}
              </Select>
            </div>

            <div>
              <Text type="secondary" style={{ display: 'block', marginBottom: '4px', fontSize: '12px' }}>Año</Text>
              <Select
                value={selectedAnio}
                onChange={setSelectedAnio}
                style={{ width: 120 }}
                size="large"
              >
                {[2024, 2025, 2026].map(anio => (
                  <Option key={anio} value={anio}>{anio}</Option>
                ))}
              </Select>
            </div>
          </Space>

          <Space size="middle">
            <Button
              icon={<ReloadOutlined />}
              onClick={cargarMetas}
              loading={loading}
              size="large"
            >
              Recargar
            </Button>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={guardarMetas}
              loading={saving}
              disabled={!hayModificaciones}
              size="large"
              style={{
                background: hayModificaciones ? '#52c41a' : undefined,
                borderColor: hayModificaciones ? '#52c41a' : undefined
              }}
            >
              {hayModificaciones ? `Guardar ${totalCambios} Cambio(s)` : 'Guardar Cambios'}
            </Button>
          </Space>
        </div>

        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={metas}
            rowKey="nombre_campana"
            pagination={false}
            size="middle"
            bordered
            rowClassName={(record) =>
              (record.nombre_campana in metasModificadas || record.nombre_campana in recaudosModificados) ? 'row-modificada' : ''
            }
            summary={() => (
              <Table.Summary fixed>
                <Table.Summary.Row style={{ backgroundColor: '#e6f7ff', fontWeight: 'bold' }}>
                  <Table.Summary.Cell index={0}>
                    <Space>
                      <Text strong style={{ fontSize: '16px', color: '#002a8d' }}>TOTAL</Text>
                      <Tag color="processing">{metas.length} subcampañas</Tag>
                    </Space>
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={1} colSpan={2}>
                    <Text strong style={{ fontSize: '18px', color: '#002a8d' }}>
                      {formatMoney(metaTotal, selectedPais)}
                    </Text>
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={3} colSpan={2} />
                </Table.Summary.Row>
              </Table.Summary>
            )}
          />
        </Spin>
      </Card>
    </div>
  );
};

export default GestionMetas;
