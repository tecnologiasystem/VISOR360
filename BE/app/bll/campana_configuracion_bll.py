from app.dal.campana_configuracion_dal import obtener_configuracion_dias, guaradar_o_actualizar_configuracion_dia
from app.utils.dias_habiles import obtener_festivos_colombia
from datetime import date, timedelta

class CampanaConfiguracionBLL:
    
    @staticmethod
    def obtener_configuracion(id_campana: int, start_date: date, end_date: date):
        """
        Obtiene la configuración combinada:
        1. Días festivos estándar de Colombia (como Inhabilitados por defecto)
        2. Configuraciones específicas de la BD (Sobreescriben el estándar)
        """
        # 1. Obtener festivos estándar en el rango
        config_map = {}
        
        # Iterar años en el rango (usualmente es un mes, así que 1 o 2 años max)
        years = set([start_date.year, end_date.year])
        festivos = []
        for y in years:
            festivos.extend(obtener_festivos_colombia(y))
        
        # Filtrar festivos dentro del rango y agregarlos como NO hábiles
        for festivo in festivos:
            if start_date <= festivo <= end_date:
                config_map[festivo] = False
        
        # 2. Obtener overrides de BD
        db_data = obtener_configuracion_dias(id_campana, start_date, end_date)
        
        # 3. Mezclar (BD tiene prioridad)
        for item in db_data:
            fecha = item["Fecha"]
            # Asegurar que sea objeto date
            if isinstance(fecha, str):
                try:
                    fecha = date.fromisoformat(fecha)
                except ValueError:
                    continue # Skip invalid dates
            elif hasattr(fecha, "date"):
                fecha = fecha.date()
            
            config_map[fecha] = item["EsHabil"]
            
        # 4. Convertir a lista para el API
        resultado = []
        for fecha, es_habil in config_map.items():
            resultado.append({
                "Fecha": fecha,
                "EsHabil": es_habil
            })
            
        return resultado
    
    @staticmethod
    def guardar_configuracion(id_campana: int, fecha: date, es_habil: bool):
        # Validaciones de negocio podrían ir aquí
        return guaradar_o_actualizar_configuracion_dia(id_campana, fecha, es_habil)
