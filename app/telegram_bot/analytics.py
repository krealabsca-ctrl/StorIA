"""Analytics para consultas del Bot de Telegram"""
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.models import TelegramQueryLog, TelegramUser, Product


class TelegramAnalytics:
    """Clase para analizar consultas del bot de Telegram"""
    
    @staticmethod
    def get_most_searched_products(days: int = 30, limit: int = 10) -> List[Dict]:
        """
        Obtener los productos más buscados en los últimos N días
        
        Args:
            days: Número de días a analizar
            limit: Límite de resultados
            
        Returns:
            Lista de diccionarios con product_id, count, product_name
        """
        db = SessionLocal()
        try:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Consulta para contar apariciones de productos en logs
            results = db.query(
                TelegramQueryLog.product_ids,
                func.count(TelegramQueryLog.id).label('search_count')
            ).filter(
                TelegramQueryLog.created_at >= since_date,
                TelegramQueryLog.product_ids.isnot(None)
            ).group_by(
                TelegramQueryLog.product_ids
            ).order_by(
                func.count(TelegramQueryLog.id).desc()
            ).limit(limit).all()
            
            # Procesar resultados
            product_stats = {}
            for result in results:
                product_ids_str = result.product_ids
                if product_ids_str:
                    product_ids = product_ids_str.split(',')
                    for pid in product_ids:
                        pid = pid.strip()
                        if pid:
                            if pid not in product_stats:
                                product_stats[pid] = 0
                            product_stats[pid] += result.search_count
            
            # Ordenar y obtener top productos
            sorted_products = sorted(
                product_stats.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:limit]
            
            # Obtener nombres de productos
            final_results = []
            for pid, count in sorted_products:
                try:
                    product = db.query(Product).filter(Product.id == int(pid)).first()
                    if product:
                        final_results.append({
                            'product_id': int(pid),
                            'product_name': product.name,
                            'product_sku': product.sku,
                            'search_count': count
                        })
                except:
                    continue
            
            return final_results
            
        finally:
            db.close()
    
    @staticmethod
    def get_most_active_users(days: int = 30, limit: int = 10) -> List[Dict]:
        """
        Obtener los usuarios más activos en los últimos N días
        
        Args:
            days: Número de días a analizar
            limit: Límite de resultados
            
        Returns:
            Lista de diccionarios con información de usuarios
        """
        db = SessionLocal()
        try:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            results = db.query(
                TelegramUser,
                func.count(TelegramQueryLog.id).label('query_count')
            ).join(
                TelegramQueryLog, TelegramUser.id == TelegramQueryLog.telegram_user_id
            ).filter(
                TelegramQueryLog.created_at >= since_date
            ).group_by(
                TelegramUser.id
            ).order_by(
                func.count(TelegramQueryLog.id).desc()
            ).limit(limit).all()
            
            user_stats = []
            for user, count in results:
                user_stats.append({
                    'telegram_id': user.telegram_id,
                    'telegram_username': user.telegram_username,
                    'telegram_first_name': user.telegram_first_name,
                    'query_count': count
                })
            
            return user_stats
            
        finally:
            db.close()
    
    @staticmethod
    def get_search_trends(days: int = 7) -> Dict:
        """
        Obtener tendencias de búsqueda por día
        
        Args:
            days: Número de días a analizar
            
        Returns:
            Diccionario con fechas y conteos
        """
        db = SessionLocal()
        try:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            results = db.query(
                func.date(TelegramQueryLog.created_at).label('date'),
                func.count(TelegramQueryLog.id).label('count')
            ).filter(
                TelegramQueryLog.created_at >= since_date
            ).group_by(
                func.date(TelegramQueryLog.created_at)
            ).order_by(
                func.date(TelegramQueryLog.created_at)
            ).all()
            
            trends = {}
            for date, count in results:
                trends[str(date)] = count
            
            return trends
            
        finally:
            db.close()
    
    @staticmethod
    def get_average_response_time(days: int = 30) -> float:
        """
        Obtener el tiempo promedio de respuesta en milisegundos
        
        Args:
            days: Número de días a analizar
            
        Returns:
            Tiempo promedio en ms
        """
        db = SessionLocal()
        try:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            result = db.query(
                func.avg(TelegramQueryLog.response_time_ms)
            ).filter(
                TelegramQueryLog.created_at >= since_date,
                TelegramQueryLog.response_time_ms.isnot(None)
            ).scalar()
            
            return round(result, 2) if result else 0.0
            
        finally:
            db.close()
    
    @staticmethod
    def get_query_type_distribution(days: int = 30) -> Dict:
        """
        Obtener distribución de tipos de consulta
        
        Args:
            days: Número de días a analizar
            
        Returns:
            Diccionario con tipos y conteos
        """
        db = SessionLocal()
        try:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            results = db.query(
                TelegramQueryLog.query_type,
                func.count(TelegramQueryLog.id).label('count')
            ).filter(
                TelegramQueryLog.created_at >= since_date
            ).group_by(
                TelegramQueryLog.query_type
            ).all()
            
            distribution = {}
            for query_type, count in results:
                distribution[query_type or 'unknown'] = count
            
            return distribution
            
        finally:
            db.close()


# Funciones de conveniencia para reportes
def generate_analytics_report(days: int = 30) -> Dict:
    """
    Generar reporte completo de analytics
    
    Args:
        days: Número de días a analizar
        
    Returns:
        Diccionario con todos los métricas
    """
    return {
        'most_searched_products': TelegramAnalytics.get_most_searched_products(days),
        'most_active_users': TelegramAnalytics.get_most_active_users(days),
        'search_trends': TelegramAnalytics.get_search_trends(days),
        'average_response_time': TelegramAnalytics.get_average_response_time(days),
        'query_type_distribution': TelegramAnalytics.get_query_type_distribution(days)
    }
