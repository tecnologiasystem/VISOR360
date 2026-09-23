import { apiClient } from './apiService';

const authService = {
  login: async (username, password) => {
    try {
      console.log('🔑 Intentando login con:', username);

      // Llamada al backend Python para login
      const loginResponse = await apiClient.post('/usuarios/login', {
        correo: username,
        clave: password
      });

      const userData = loginResponse.data;
      console.log('🔑 Respuesta del backend:', userData);
      console.log('🔑 Campañas recibidas del backend:', userData.campanas);
      console.log('🔑 Inversionistas recibidos del backend:', userData.inversionistas);

      // Crear token mock
      const mockToken = 'mock-jwt-token-' + userData.UsuarioID;

      const userComplete = {
        id: userData.UsuarioID,
        username: username,
        name: userData.nombre || username.split('@')[0],
        email: userData.email || username,
        rol_nombre: userData.rol_nombre || 'Usuario',
        torre_control: userData.torre_control || false,
        financiero: userData.financiero || false,
        recursos_humanos: userData.recursos_humanos || false,
        gestion_metas: userData.gestion_metas || false,
        gestion_usuarios: userData.gestion_usuarios || false,
        campanas: userData.campanas || [],
        inversionistas: userData.inversionistas || [],
        // Mantener compatibilidad con código existente
        permisos: {
          torre_de_control: userData.torre_control || false,
          financiero: userData.financiero || false,
          recursos_humanos: userData.recursos_humanos || false,
          metas: userData.gestion_metas || false
        },
        permissions: [],
        roles: [userData.rol_nombre || 'Usuario']
      };

      console.log('🔑 Usuario completo a guardar:', userComplete);

      return {
        token: mockToken,
        user: userComplete,
      };
    } catch (error) {
      console.error('Error en login:', error);
      throw new Error(error.response?.data?.detail || 'Credenciales inválidas');
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  hasPermission: (permission) => {
    const user = authService.getCurrentUser();
    return user?.permissions?.includes(permission) || false;
  },

  hasRole: (role) => {
    const user = authService.getCurrentUser();
    return user?.roles?.includes(role) || false;
  },
};

export default authService;
