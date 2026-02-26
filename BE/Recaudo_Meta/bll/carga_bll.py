"""
BLL para Carga de Recaudo
Lógica de negocio para cargas desde Excel/Staging
"""
from typing import List, Optional, Dict, Any
import logging
from dal import carga_dal
from models.carga import (
    CargaDesdeExcelRequest,
    CargaRecaudoResponse,
    CargaRecaudo,
    CargaRecaudoListResponse,
    OrigenCarga
)
from database import DatabaseError

logger = logging.getLogger(__name__)


class CargaRecaudoService:
    """Servicio de lógica de negocio para Cargas de Recaudo"""
    
    @staticmethod
    def ejecutar_carga_desde_staging(
        request: CargaDesdeExcelRequest
    ) -> CargaRecaudoResponse:
        """
        Ejecuta el proceso de carga desde staging.
        
        Asume que los datos ya fueron cargados en CampanasRecaudoStagingQA.
        Llama al SP_CampanasRecaudoQA_CargarDesdeStaging que:
        - Mapea nombres de campañas
        - Limpia valores numéricos
        - Hace MERGE sobre CampanasRecaudoDiarioQA
        - Registra la carga en CampanasRecaudoCargaQA
        
        Args:
            request: Datos de la carga
        
        Returns:
            CargaRecaudoResponse con resultado
        """
        try:
            # Validar que hay datos en staging
            count_staging = carga_dal.contar_staging()
            if count_staging == 0:
                return CargaRecaudoResponse(
                    success=False,
                    IDCargaRecaudoQA=0,
                    FilasAfectadas=0,
                    message="No hay datos en staging para procesar"
                )
            
            logger.info(f"Iniciando carga desde staging. Filas en staging: {count_staging}")
            
            # Ejecutar el SP de carga
            resultado = carga_dal.sp_cargar_desde_staging(
                nombre_archivo=request.NombreArchivo,
                id_usuario_carga=request.IDUsuarioCarga,
                ruta_archivo=request.RutaArchivo,
                origen=request.Origen.value if isinstance(request.Origen, OrigenCarga) else request.Origen,
                periodo_anio_mes=request.PeriodoAnioMes
            )
            
            # Limpiar staging después de cargar exitosamente
            carga_dal.limpiar_staging()
            
            return CargaRecaudoResponse(
                success=True,
                IDCargaRecaudoQA=resultado.get("IDCargaRecaudoQA") or 0,
                FilasAfectadas=resultado.get("FilasAfectadas") or 0,
                PeriodoAnioMes=resultado.get("PeriodoAnioMes"),
                message=f"Carga completada exitosamente. {resultado.get('FilasAfectadas', 0)} registros procesados."
            )
            
        except DatabaseError as e:
            logger.error(f"Error en carga desde staging: {e}")
            return CargaRecaudoResponse(
                success=False,
                IDCargaRecaudoQA=0,
                FilasAfectadas=0,
                message=f"Error en la carga: {str(e)}"
            )
    
    @staticmethod
    def cargar_datos_a_staging(filas: List[dict]) -> Dict[str, Any]:
        """
        Carga datos a la tabla de staging.
        
        Args:
            filas: Lista de diccionarios con datos del Excel
                Cada fila debe tener: Campana, AnioMes, DiaHabil, ValorRecaudo, Inversionista, Meta
        
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Limpiar staging primero
            eliminados = carga_dal.limpiar_staging()
            logger.info(f"Staging limpiado: {eliminados} filas eliminadas")
            
            # Insertar nuevos datos
            insertados = carga_dal.insertar_en_staging(filas)
            
            return {
                "success": True,
                "filas_insertadas": insertados,
                "filas_limpiadas": eliminados,
                "message": f"Se cargaron {insertados} filas al staging"
            }
            
        except DatabaseError as e:
            logger.error(f"Error al cargar staging: {e}")
            return {
                "success": False,
                "filas_insertadas": 0,
                "message": f"Error al cargar staging: {str(e)}"
            }
    
    @staticmethod
    def obtener_preview_staging(limite: int = 100) -> Dict[str, Any]:
        """
        Obtiene una vista previa de los datos en staging.
        
        Args:
            limite: Número máximo de filas
        
        Returns:
            Dict con preview y conteo
        """
        try:
            total = carga_dal.contar_staging()
            preview = carga_dal.get_staging_preview(limite)
            
            return {
                "success": True,
                "total": total,
                "preview": preview,
                "showing": len(preview)
            }
        except DatabaseError as e:
            logger.error(f"Error al obtener preview: {e}")
            return {
                "success": False,
                "total": 0,
                "preview": [],
                "message": str(e)
            }
    
    @staticmethod
    def obtener_historial_cargas(
        id_usuario: Optional[int] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        limite: int = 100
    ) -> CargaRecaudoListResponse:
        """
        Obtiene el historial de cargas.
        
        Returns:
            CargaRecaudoListResponse con lista de cargas
        """
        try:
            cargas_raw = carga_dal.get_cargas_recaudo(
                id_usuario=id_usuario,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                limite=limite
            )
            
            cargas = [
                CargaRecaudo(
                    IDCargaRecaudoQA=c["IDCargaRecaudoQA"],
                    PeriodoAnioMes=c.get("PeriodoAnioMes"),
                    NombreArchivo=c.get("NombreArchivo"),
                    RutaArchivo=c.get("RutaArchivo"),
                    FechaCarga=c["FechaCarga"],
                    IDUsuarioCarga=c["IDUsuarioCarga"],
                    Origen=OrigenCarga(c.get("Origen", "EXCEL")),
                    Observaciones=c.get("Observaciones")
                ) for c in cargas_raw
            ]
            
            return CargaRecaudoListResponse(
                success=True,
                data=cargas,
                total=len(cargas)
            )
        except DatabaseError as e:
            logger.error(f"Error al obtener historial de cargas: {e}")
            raise
    
    @staticmethod
    def obtener_carga_por_id(id_carga: int) -> Optional[CargaRecaudo]:
        """
        Obtiene una carga por ID.
        
        Args:
            id_carga: ID de la carga
        
        Returns:
            CargaRecaudo o None
        """
        try:
            data = carga_dal.get_carga_by_id(id_carga)
            if data:
                return CargaRecaudo(
                    IDCargaRecaudoQA=data["IDCargaRecaudoQA"],
                    PeriodoAnioMes=data.get("PeriodoAnioMes"),
                    NombreArchivo=data.get("NombreArchivo"),
                    RutaArchivo=data.get("RutaArchivo"),
                    FechaCarga=data["FechaCarga"],
                    IDUsuarioCarga=data["IDUsuarioCarga"],
                    Origen=OrigenCarga(data.get("Origen", "EXCEL")),
                    Observaciones=data.get("Observaciones")
                )
            return None
        except DatabaseError as e:
            logger.error(f"Error al obtener carga {id_carga}: {e}")
            raise
    
    @staticmethod
    def obtener_registros_de_carga(id_carga: int) -> List[dict]:
        """
        Obtiene los registros de recaudo asociados a una carga.
        
        Args:
            id_carga: ID de la carga
        
        Returns:
            Lista de registros
        """
        try:
            return carga_dal.get_registros_por_carga(id_carga)
        except DatabaseError as e:
            logger.error(f"Error al obtener registros de carga {id_carga}: {e}")
            raise
    
    @staticmethod
    def obtener_auditoria(
        id_recaudo: Optional[int] = None,
        id_carga: Optional[int] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        limite: int = 100
    ) -> List[dict]:
        """
        Obtiene registros de auditoría.
        
        Returns:
            Lista de registros de auditoría
        """
        try:
            return carga_dal.get_auditoria_recaudo(
                id_recaudo=id_recaudo,
                id_carga=id_carga,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                limite=limite
            )
        except DatabaseError as e:
            logger.error(f"Error al obtener auditoría: {e}")
            raise
