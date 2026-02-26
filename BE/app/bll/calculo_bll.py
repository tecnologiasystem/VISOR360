from datetime import datetime
from fastapi import HTTPException
from app.dal.calculo_dal import obtener_recaudo_por_dia, obtener_recaudo_por_mes, obtener_recaudo_ultimos_4_meses

class CalculoBLL:

    @staticmethod
    def buscar_recaudo_por_dia(campana: str = None, mes: int = None, dia_corte: int = None, year: int = None):
        hoy = datetime.now()
        
        if year is None:
            year = hoy.year
        
        if mes and (mes < 1 or mes > 12):
            raise HTTPException(status_code=400, detail="El mes debe estar entre 1 y 12")
        
        if dia_corte and dia_corte not in [1, 10, 20]:
            raise HTTPException(status_code=400, detail="El día de corte debe ser 1, 10 o 20")
        
        if mes:
            fecha_consulta = datetime(year, mes, 1)
            diferencia = hoy - fecha_consulta
            if diferencia.days > 120:
                raise HTTPException(status_code=400, detail="Solo puedes consultar hasta 4 meses atrás")

        datos = obtener_recaudo_por_dia(
            nombre_campana=campana,
            mes=mes,
            dia_corte=dia_corte,
            year=year
        )

        # La consulta ahora devuelve solo el total en una fila
        total_usd = round(float(datos[0][0]), 2) if datos and datos[0][0] is not None else 0.0

        return {
            "filtros": {
                "campana": campana,
                "mes": mes,
                "dia_corte": dia_corte,
                "year": year
            },
            "total_usd": total_usd
        }

    @staticmethod
    def buscar_recaudo_por_mes(campana: str = None, mes: int = None, year: int = None):
        hoy = datetime.now()
        
        if year is None:
            year = hoy.year
        
        if mes and (mes < 1 or mes > 12):
            raise HTTPException(status_code=400, detail="El mes debe estar entre 1 y 12")
        
        if mes:
            fecha_consulta = datetime(year, mes, 1)
            diferencia = hoy - fecha_consulta
            if diferencia.days > 120:
                raise HTTPException(status_code=400, detail="Solo puedes consultar hasta 4 meses atrás")

        datos = obtener_recaudo_por_mes(
            nombre_campana=campana,
            mes=mes,
            year=year
        )

        resultado = [
            {
                "fecha": str(row[0]),
                "total_usd": round(float(row[1]), 2)
            }
            for row in datos
        ]

        return {
            "total_registros": len(resultado),
            "filtros": {
                "campana": campana,
                "mes": mes,
                "year": year
            },
            "datos": resultado
        }
  
    @staticmethod
    def buscar_recaudo_ultimos_4_meses(campana: str = None, year: int = None):
        hoy = datetime.now()
        
        if year is None:
            year = hoy.year

        # Validar que no se pase de 4 meses atrás (agosto del año en curso)
        fecha_agosto = datetime(year, 8, 1)
        diferencia = hoy - fecha_agosto
        if diferencia.days > 120:
            raise HTTPException(status_code=400, detail="Solo puedes consultar hasta 4 meses atrás desde agosto")

        datos = obtener_recaudo_ultimos_4_meses(
            nombre_campana=campana,
            year=year
            
        )

        # Nombres de los meses
        meses_nombres = {
            8: "Agosto",
            9: "Septiembre",
            10: "Octubre",
            11: "Noviembre"
        }

        # Procesar datos por mes
        resultado_por_mes = [
            {
                "mes": row[0],
                "nombre_mes": meses_nombres.get(row[0], f"Mes {row[0]}"),
                "total_usd": round(float(row[1]), 2)
            }
            for row in datos
        ]

        # Calcular total general
        total_general = sum(item["total_usd"] for item in resultado_por_mes)

        return {
            "filtros": {
                "campana": campana,
                "meses": "8-11 (Agosto-Noviembre)",
                "year": year
            },
            "recaudo_por_mes": resultado_por_mes,
            "total_usd": round(total_general, 2)
        }
    