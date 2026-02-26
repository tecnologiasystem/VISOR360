import React, { useState, useEffect, useMemo } from 'react';
import {
  Card, Table, Button, Modal, Form, Input, Select, Transfer,
  message, Space, Tag, Tabs, Checkbox, Spin, Tooltip, Popconfirm, Tree, Switch
} from 'antd';
import {
  UserAddOutlined, EditOutlined, DeleteOutlined, TeamOutlined,
  ApartmentOutlined, DollarOutlined, SafetyOutlined, ReloadOutlined,
  SearchOutlined, SafetyCertificateOutlined, DashboardOutlined
} from '@ant-design/icons';
import api from '../api';
import './GestionPermisos.css';

const { Option } = Select;
const { TabPane } = Tabs;

const PermissionCard = ({ title, icon, description, checked, onChange, danger }) => (
  <div
    className={`permission-card ${checked ? 'active' : ''} ${danger ? 'danger' : ''}`}
    onClick={() => onChange(!checked)}
  >
    <div className="permission-icon">
      {icon}
    </div>
    <div className="permission-info">
      <div className="permission-header">
        <span className="permission-title">{title}</span>
        <Switch
          checked={checked}
          onChange={onChange}
          size="small"
          className={danger ? 'danger-switch' : ''}
        />
      </div>
      <p className="permission-desc">{description}</p>
    </div>
  </div>
);

const GestionPermisos = () => {
  // Estados
  const [loading, setLoading] = useState(false);
  const [usuarios, setUsuarios] = useState([]);
  const [roles, setRoles] = useState([]);
  const [campanas, setCampanas] = useState([]);
  const [inversionistas, setInversionistas] = useState([]);

  // Modals
  const [modalUsuario, setModalUsuario] = useState({ visible: false, modo: 'crear', data: null });
  const [modalRol, setModalRol] = useState({ visible: false, modo: 'crear', data: null });
  const [modalCampanas, setModalCampanas] = useState({ visible: false, rolId: null, rolNombre: '' });

  // Forms
  const [formUsuario] = Form.useForm();
  const [formRol] = Form.useForm();

  // Transfer (para asignar campañas a roles)
  const [targetKeys, setTargetKeys] = useState([]);
  const [checkedKeys, setCheckedKeys] = useState([]);
  const [expandedKeys, setExpandedKeys] = useState([]);

  // Estados de búsqueda
  const [searchTextUsuarios, setSearchTextUsuarios] = useState({});
  const [searchTextRoles, setSearchTextRoles] = useState({});

  // ==================== CARGA INICIAL ====================

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    setLoading(true);
    try {
      await Promise.all([
        cargarUsuarios(),
        cargarRoles(),
        cargarCampanas(),
        cargarInversionistas()
      ]);
    } catch (error) {
      message.error('Error al cargar los datos');
    } finally {
      setLoading(false);
    }
  };

  const cargarUsuarios = async () => {
    try {
      const response = await api.get('/permisos/usuarios');
      setUsuarios(response.data.data || []);
    } catch (error) {
      console.error('Error al cargar usuarios:', error);
      throw error;
    }
  };

  const cargarRoles = async () => {
    try {
      const response = await api.get('/permisos/roles');
      setRoles(response.data.data || []);
    } catch (error) {
      console.error('Error al cargar roles:', error);
      throw error;
    }
  };

  const cargarCampanas = async () => {
    try {
      const response = await api.get('/permisos/campanas');
      setCampanas(response.data.data || []);
    } catch (error) {
      console.error('Error al cargar campañas:', error);
      throw error;
    }
  };

  const cargarInversionistas = async () => {
    try {
      const response = await api.get('/permisos/inversionistas');
      setInversionistas(response.data.data || []);
    } catch (error) {
      console.error('Error al cargar inversionistas:', error);
      throw error;
    }
  };

  // ==================== USUARIOS ====================

  const abrirModalUsuario = (modo, usuario = null) => {
    setModalUsuario({ visible: true, modo, data: usuario });

    if (modo === 'editar' && usuario) {
      formUsuario.setFieldsValue({
        nombre: usuario.nombre,
        email: usuario.email,
        id_rol: usuario.id_rol
      });
    } else {
      formUsuario.resetFields();
    }
  };

  const cerrarModalUsuario = () => {
    setModalUsuario({ visible: false, modo: 'crear', data: null });
    formUsuario.resetFields();
  };

  const guardarUsuario = async () => {
    try {
      const values = await formUsuario.validateFields();

      if (modalUsuario.modo === 'crear') {
        await api.post('/permisos/usuarios', values);
        message.success('Usuario creado exitosamente');
      } else {
        await api.put(`/permisos/usuarios/${modalUsuario.data.id_usuario}`, values);
        message.success('Usuario actualizado exitosamente');
      }

      cerrarModalUsuario();
      cargarUsuarios();
    } catch (error) {
      if (error.errorFields) {
        // Error de validación del formulario
        return;
      }
      message.error(error.response?.data?.detail || 'Error al guardar usuario');
    }
  };

  const eliminarUsuario = async (id) => {
    try {
      await api.delete(`/permisos/usuarios/${id}`);
      message.success('Usuario eliminado exitosamente');
      cargarUsuarios();
    } catch (error) {
      message.error(error.response?.data?.detail || 'Error al eliminar usuario');
    }
  };

  // ==================== ROLES ====================

  const abrirModalRol = (modo, rol = null) => {
    setModalRol({ visible: true, modo, data: rol });

    if (modo === 'editar' && rol) {
      formRol.setFieldsValue({
        nombre_rol: rol.nombre_rol,
        torre_control: rol.torre_control,
        financiero: rol.financiero,
        recursos_humanos: rol.recursos_humanos,
        gestion_usuarios: rol.gestion_usuarios,
        gestion_metas: rol.gestion_metas
      });
    } else {
      formRol.resetFields();
    }
  };

  const cerrarModalRol = () => {
    setModalRol({ visible: false, modo: 'crear', data: null });
    formRol.resetFields();
  };

  const guardarRol = async () => {
    try {
      const values = await formRol.validateFields();

      if (modalRol.modo === 'crear') {
        await api.post('/permisos/roles', values);
        message.success('Rol creado exitosamente');
      } else {
        await api.put(`/permisos/roles/${modalRol.data.id_rol}`, values);
        message.success('Rol actualizado exitosamente');
      }

      cerrarModalRol();
      cargarRoles();
      cargarUsuarios(); // Recargar usuarios para ver cambios en permisos
    } catch (error) {
      if (error.errorFields) {
        return;
      }
      message.error(error.response?.data?.detail || 'Error al guardar rol');
    }
  };

  const eliminarRol = async (id) => {
    try {
      await api.delete(`/permisos/roles/${id}`);
      message.success('Rol eliminado exitosamente');
      cargarRoles();
    } catch (error) {
      message.error(error.response?.data?.detail || 'Error al eliminar rol');
    }
  };

  // ==================== ASIGNACIÓN DE CAMPAÑAS ====================

  const abrirModalCampanas = async (rol) => {
    setModalCampanas({ visible: true, rolId: rol.id_rol, rolNombre: rol.nombre_rol });

    try {
      // Cargar inversionistas ya asignados a este rol
      const response = await api.get(`/permisos/roles/${rol.id_rol}/campanas`);
      const inversionistasAsignados = response.data.data || [];
      const idsAsignados = inversionistasAsignados.map(inv => `inv-${inv.id_inversionista}`);
      setCheckedKeys(idsAsignados);

      // Expandir todas las campañas grandes dinámicamente
      const campanasUnicas = [...new Set(inversionistas.map(inv => inv.nombre_campana).filter(Boolean))];
      setExpandedKeys(campanasUnicas);
    } catch (error) {
      message.error('Error al cargar campañas del rol');
      setCheckedKeys([]);
    }
  };

  const cerrarModalCampanas = () => {
    setModalCampanas({ visible: false, rolId: null, rolNombre: '' });
    setCheckedKeys([]);
    setExpandedKeys([]);
  };

  const guardarCampanas = async () => {
    try {
      console.log('🔍 DEBUG Guardar Campañas:');
      console.log('  - Rol ID:', modalCampanas.rolId);
      console.log('  - Checked keys:', checkedKeys);

      // SOLO extraer IDs de inversionistas que están en checkedKeys
      const inversionistasIds = checkedKeys
        .filter(key => key.startsWith('inv-'))
        .map(key => parseInt(key.replace('inv-', '')));

      console.log('  - Inversionistas IDs seleccionados:', inversionistasIds);

      if (inversionistasIds.length === 0) {
        message.warning('Debes seleccionar al menos un inversionista');
        return;
      }

      // Deducir las campañas ÚNICAMENTE desde los inversionistas seleccionados
      const campanasDeInversionistas = new Set();
      inversionistasIds.forEach(invId => {
        const inv = inversionistas.find(i => i.id_inversionista === invId);
        if (inv && inv.nombre_campana) {
          campanasDeInversionistas.add(inv.nombre_campana);
        }
      });

      // Buscar los IDs de las campañas
      const idsCampanas = Array.from(campanasDeInversionistas).map(nombreCampana => {
        const campanaData = campanas.find(c => c.nombre_campana === nombreCampana);
        return campanaData?.id_campana;
      }).filter(id => id != null);

      console.log('  - Campañas deducidas:', Array.from(campanasDeInversionistas));
      console.log('  - IDs campañas finales:', idsCampanas);
      console.log('  - IDs inversionistas finales:', inversionistasIds);

      // Enviar campañas E inversionistas seleccionados
      const payload = {
        ids_campanas: idsCampanas,
        ids_inversionistas: inversionistasIds
      };

      console.log('📤 Payload a enviar:', payload);

      const response = await api.put(`/permisos/roles/${modalCampanas.rolId}/campanas`, payload);

      console.log('✅ Respuesta del servidor:', response.data);
      message.success('Campañas e inversionistas actualizados exitosamente');
      cerrarModalCampanas();
      cargarRoles(); // Recargar roles para ver cambios
    } catch (error) {
      console.error('❌ Error al guardar campañas:', error);
      message.error(error.response?.data?.detail || 'Error al actualizar campañas');
    }
  };

  // ==================== ÁRBOL DE CAMPAÑAS ====================

  const arbolCampanas = useMemo(() => {
    // Agrupar inversionistas por campaña dinámicamente (con deduplicación)
    const campanasMap = {};
    const inversionistasVistos = new Set();

    // Filtrar y agrupar inversionistas sin duplicados
    inversionistas.forEach(inv => {
      const campana = inv.nombre_campana;
      const invId = inv.id_inversionista;

      // Evitar duplicados por ID de inversionista
      if (!campana || inversionistasVistos.has(invId)) return;

      inversionistasVistos.add(invId);

      if (!campanasMap[campana]) {
        campanasMap[campana] = [];
      }

      campanasMap[campana].push({
        title: inv.nombre_inversionista,
        key: `inv-${invId}`,
        isLeaf: true
      });
    });

    // Construir árbol solo con campañas que tienen inversionistas
    return Object.keys(campanasMap)
      .filter(campana => campanasMap[campana].length > 0)
      .sort()
      .map(campana => ({
        title: <strong>{campana}</strong>,
        key: campana,
        children: campanasMap[campana].sort((a, b) => a.title.localeCompare(b.title))
      }));
  }, [inversionistas]);

  const onCheckCampanas = (checkedKeysValue) => {
    // Guardar TODAS las claves seleccionadas (campañas e inversionistas)
    // La función guardarCampanas se encargará de extraer los inversionistas correctos
    console.log('📋 Claves seleccionadas:', checkedKeysValue);
    setCheckedKeys(checkedKeysValue);
  };

  // ==================== BÚSQUEDA EN COLUMNAS ====================

  const getColumnSearchProps = (dataIndex, searchText, setSearchText, campo) => ({
    filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => (
      <div style={{ padding: 8 }}>
        <Input
          placeholder={`Buscar ${campo}`}
          value={selectedKeys[0]}
          onChange={e => setSelectedKeys(e.target.value ? [e.target.value] : [])}
          onPressEnter={() => {
            confirm();
            setSearchText({ ...searchText, [dataIndex]: selectedKeys[0] });
          }}
          style={{ marginBottom: 8, display: 'block' }}
        />
        <Space>
          <Button
            type="primary"
            onClick={() => {
              confirm();
              setSearchText({ ...searchText, [dataIndex]: selectedKeys[0] });
            }}
            icon={<SearchOutlined />}
            size="small"
            style={{ width: 90 }}
          >
            Buscar
          </Button>
          <Button
            onClick={() => {
              clearFilters();
              setSearchText({ ...searchText, [dataIndex]: '' });
              confirm();
            }}
            size="small"
            style={{ width: 90 }}
          >
            Limpiar
          </Button>
        </Space>
      </div>
    ),
    filterIcon: filtered => <SearchOutlined style={{ color: filtered ? '#1890ff' : undefined }} />,
    onFilter: (value, record) => {
      const val = record[dataIndex];
      return val ? val.toString().toLowerCase().includes(value.toLowerCase()) : false;
    }
  });

  // ==================== COLUMNAS TABLAS ====================

  const columnasUsuarios = [
    {
      title: 'ID',
      dataIndex: 'id_usuario',
      key: 'id_usuario',
      width: 60,
      sorter: (a, b) => a.id_usuario - b.id_usuario
    },
    {
      title: 'Nombre',
      dataIndex: 'nombre',
      key: 'nombre',
      sorter: (a, b) => a.nombre.localeCompare(b.nombre),
      ...getColumnSearchProps('nombre', searchTextUsuarios, setSearchTextUsuarios, 'nombre')
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      sorter: (a, b) => a.email.localeCompare(b.email),
      ...getColumnSearchProps('email', searchTextUsuarios, setSearchTextUsuarios, 'email')
    },
    {
      title: 'Rol',
      dataIndex: 'nombre_rol',
      key: 'nombre_rol',
      render: (text) => <Tag color="blue">{text || 'Sin rol'}</Tag>,
      ...getColumnSearchProps('nombre_rol', searchTextUsuarios, setSearchTextUsuarios, 'rol')
    },
    {
      title: 'Permisos Módulos',
      key: 'permisos',
      render: (_, record) => (
        <Space size={4}>
          {record.permisos_modulos?.torre_control && (
            <Tooltip title="Torre de Control">
              <Tag color="green" icon={<ApartmentOutlined />}>Torre</Tag>
            </Tooltip>
          )}
          {record.permisos_modulos?.financiero && (
            <Tooltip title="Financiero">
              <Tag color="gold" icon={<DollarOutlined />}>Financiero</Tag>
            </Tooltip>
          )}
          {record.permisos_modulos?.recursos_humanos && (
            <Tooltip title="Recursos Humanos">
              <Tag color="purple" icon={<TeamOutlined />}>RRHH</Tag>
            </Tooltip>
          )}
        </Space>
      )
    },
    {
      title: 'Acciones',
      key: 'acciones',
      width: 120,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => abrirModalUsuario('editar', record)}
          />
          <Popconfirm
            title="¿Eliminar usuario?"
            description="Esta acción no se puede deshacer"
            onConfirm={() => eliminarUsuario(record.id_usuario)}
            okText="Eliminar"
            cancelText="Cancelar"
            okButtonProps={{ danger: true }}
          >
            <Button type="link" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      )
    }
  ];

  const columnasRoles = [
    {
      title: 'ID',
      dataIndex: 'id_rol',
      key: 'id_rol',
      width: 60,
      sorter: (a, b) => a.id_rol - b.id_rol
    },
    {
      title: 'Nombre Rol',
      dataIndex: 'nombre_rol',
      key: 'nombre_rol',
      sorter: (a, b) => a.nombre_rol.localeCompare(b.nombre_rol),
      ...getColumnSearchProps('nombre_rol', searchTextRoles, setSearchTextRoles, 'rol')
    },
    {
      title: 'Torre de Control',
      dataIndex: 'torre_control',
      key: 'torre_control',
      width: 150,
      render: (val) => val ? <Tag color="green">Sí</Tag> : <Tag>No</Tag>,
      filters: [
        { text: 'Sí', value: true },
        { text: 'No', value: false }
      ],
      onFilter: (value, record) => record.torre_control === value
    },
    {
      title: 'Financiero',
      dataIndex: 'financiero',
      key: 'financiero',
      width: 120,
      render: (val) => val ? <Tag color="green">Sí</Tag> : <Tag>No</Tag>,
      filters: [
        { text: 'Sí', value: true },
        { text: 'No', value: false }
      ],
      onFilter: (value, record) => record.financiero === value
    },
    {
      title: 'RRHH',
      dataIndex: 'recursos_humanos',
      key: 'recursos_humanos',
      width: 100,
      render: (val) => val ? <Tag color="green">Sí</Tag> : <Tag>No</Tag>,
      filters: [
        { text: 'Sí', value: true },
        { text: 'No', value: false }
      ],
      onFilter: (value, record) => record.recursos_humanos === value
    },
    {
      title: 'Metas',
      dataIndex: 'gestion_metas',
      key: 'gestion_metas',
      width: 100,
      render: (val) => val ? <Tag color="green">Sí</Tag> : <Tag>No</Tag>,
      filters: [
        { text: 'Sí', value: true },
        { text: 'No', value: false }
      ],
      onFilter: (value, record) => record.gestion_metas === value
    },
    {
      title: 'Permisos',
      dataIndex: 'gestion_usuarios',
      key: 'gestion_usuarios',
      width: 100,
      render: (val) => val ? <Tag color="green">Sí</Tag> : <Tag>No</Tag>,
      filters: [
        { text: 'Sí', value: true },
        { text: 'No', value: false }
      ],
      onFilter: (value, record) => record.gestion_usuarios === value
    },
    {
      title: 'Acciones',
      key: 'acciones',
      width: 180,
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<ApartmentOutlined />}
            onClick={() => abrirModalCampanas(record)}
          >
            Campañas
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => abrirModalRol('editar', record)}
          />
          <Popconfirm
            title="¿Eliminar rol?"
            description="Solo se puede eliminar si no tiene usuarios asignados"
            onConfirm={() => eliminarRol(record.id_rol)}
            okText="Eliminar"
            cancelText="Cancelar"
            okButtonProps={{ danger: true }}
          >
            <Button type="link" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      )
    }
  ];

  // ==================== RENDER ====================

  return (
    <div className="gestion-permisos-container">
      <Card
        title={
          <Space>
            <SafetyOutlined style={{ fontSize: 24, color: '#1890ff' }} />
            <span>Gestión de Permisos y Usuarios</span>
          </Space>
        }
        extra={
          <Button
            icon={<ReloadOutlined />}
            onClick={cargarDatos}
            loading={loading}
          >
            Recargar
          </Button>
        }
      >
        <Tabs defaultActiveKey="usuarios">
          {/* TAB USUARIOS */}
          <TabPane
            tab={<span><TeamOutlined />Usuarios</span>}
            key="usuarios"
          >
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <Button
                type="primary"
                icon={<UserAddOutlined />}
                onClick={() => abrirModalUsuario('crear')}
              >
                Nuevo Usuario
              </Button>

              <Table
                columns={columnasUsuarios}
                dataSource={usuarios}
                rowKey="id_usuario"
                loading={loading}
                pagination={{ pageSize: 10 }}
                size="small"
              />
            </Space>
          </TabPane>

          {/* TAB ROLES */}
          <TabPane
            tab={<span><SafetyOutlined />Roles</span>}
            key="roles"
          >
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <Button
                type="primary"
                icon={<UserAddOutlined />}
                onClick={() => abrirModalRol('crear')}
              >
                Nuevo Rol
              </Button>

              <Table
                columns={columnasRoles}
                dataSource={roles}
                rowKey="id_rol"
                loading={loading}
                pagination={{ pageSize: 10 }}
                size="small"
              />
            </Space>
          </TabPane>
        </Tabs>
      </Card>

      {/* MODAL USUARIO */}
      <Modal
        title={modalUsuario.modo === 'crear' ? 'Nuevo Usuario' : 'Editar Usuario'}
        open={modalUsuario.visible}
        onOk={guardarUsuario}
        onCancel={cerrarModalUsuario}
        okText="Guardar"
        cancelText="Cancelar"
      >
        <Form form={formUsuario} layout="vertical">
          <Form.Item
            name="nombre"
            label="Nombre Completo"
            rules={[{ required: true, message: 'Ingrese el nombre' }]}
          >
            <Input placeholder="Juan Pérez" />
          </Form.Item>

          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Ingrese el email' },
              { type: 'email', message: 'Email inválido' }
            ]}
          >
            <Input placeholder="juan.perez@ejemplo.com" />
          </Form.Item>

          <Form.Item
            name="id_rol"
            label="Rol"
            rules={[{ required: true, message: 'Seleccione un rol' }]}
          >
            <Select placeholder="Seleccione un rol">
              {roles.map(rol => (
                <Option key={rol.id_rol} value={rol.id_rol}>
                  {rol.nombre_rol}
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* MODAL ROL */}
      <Modal
        title={modalRol.modo === 'crear' ? 'Nuevo Rol' : 'Editar Rol'}
        open={modalRol.visible}
        onOk={guardarRol}
        onCancel={cerrarModalRol}
        okText="Guardar"
        cancelText="Cancelar"
      >
        <Form form={formRol} layout="vertical" className="role-form">
          <Form.Item
            name="nombre_rol"
            label="Nombre del Rol"
            rules={[{ required: true, message: 'Ingrese el nombre del rol' }]}
          >
            <Input size="large" placeholder="Ej: Analista Financiero" prefix={<SafetyOutlined />} />
          </Form.Item>

          <div className="permissions-section">
            <h3 className="section-title">Permisos de Acceso</h3>
            <p className="section-subtitle">Define a qué módulos tendrá acceso este rol</p>

            <div className="permissions-grid">
              {/* Torre de Control */}
              <Form.Item name="torre_control" valuePropName="checked" noStyle>
                <PermissionCard
                  title="Torre de Control"
                  icon={<ApartmentOutlined />}
                  description="Acceso a tableros de control y KPIs operativos."
                />
              </Form.Item>

              {/* Financiero */}
              <Form.Item name="financiero" valuePropName="checked" noStyle>
                <PermissionCard
                  title="Análisis Financiero"
                  icon={<DollarOutlined />}
                  description="Visualización de métricas y reportes financieros."
                />
              </Form.Item>

              {/* RRHH */}
              <Form.Item name="recursos_humanos" valuePropName="checked" noStyle>
                <PermissionCard
                  title="Talento Humano"
                  icon={<TeamOutlined />}
                  description="Gestión de personal, radar de talento y board de RH."
                />
              </Form.Item>

              {/* Metas */}
              <Form.Item name="gestion_metas" valuePropName="checked" noStyle>
                <PermissionCard
                  title="Gestión de Metas"
                  icon={<DashboardOutlined />}
                  description="Configuración y seguimiento de metas corporativas."
                />
              </Form.Item>

              {/* Permisos (Antes Gestión de Usuarios) */}
              <Form.Item name="gestion_usuarios" valuePropName="checked" noStyle>
                <PermissionCard
                  title="Permisos"
                  icon={<SafetyCertificateOutlined />}
                  description="Administración de usuarios, roles y accesos del sistema."
                  danger
                />
              </Form.Item>
            </div>
          </div>
        </Form>
      </Modal>

      {/* MODAL ASIGNAR CAMPAÑAS */}
      <Modal
        title={`Asignar Campañas al Rol: ${modalCampanas.rolNombre}`}
        open={modalCampanas.visible}
        onOk={guardarCampanas}
        onCancel={cerrarModalCampanas}
        okText="Guardar"
        cancelText="Cancelar"
        width={600}
      >
        <div style={{ marginBottom: 16 }}>
          <Tag color="blue">💡 Tip:</Tag>
          <span style={{ fontSize: 12, color: '#666' }}>
            Puedes seleccionar campañas completas o inversionistas individuales
          </span>
        </div>

        <Tree
          checkable
          defaultExpandAll
          expandedKeys={expandedKeys}
          onExpand={setExpandedKeys}
          checkedKeys={checkedKeys}
          onCheck={onCheckCampanas}
          treeData={arbolCampanas}
          height={400}
          showLine={{ showLeafIcon: false }}
          style={{ border: '1px solid #d9d9d9', borderRadius: 4, padding: 12 }}
        />

        <div style={{ marginTop: 16, fontSize: 12, color: '#666' }}>
          <strong>Seleccionados:</strong> {checkedKeys.filter(k => k.startsWith('inv-')).length} inversionista(s)
        </div>
      </Modal>
    </div>
  );
};

export default GestionPermisos;
