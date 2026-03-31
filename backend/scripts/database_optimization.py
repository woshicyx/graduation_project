#!/usr/bin/env python3
"""
数据库优化脚本 - 提供性能优化建议和执行优化操作
"""

import os
import sys
import psycopg2
import logging
from typing import Dict, List, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """数据库优化器"""
    
    def __init__(self, password="356921"):
        """初始化优化器"""
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'user': 'postgres',
            'password': password,
            'database': 'movie_recommendation'
        }
        self.conn = None
        self.cursor = None
    
    def connect(self) -> bool:
        """连接到数据库"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            logger.info("✅ 数据库连接成功")
            return True
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("数据库连接已关闭")
    
    def analyze_database_health(self) -> Dict:
        """分析数据库健康状况"""
        try:
            logger.info("分析数据库健康状况...")
            
            health_report = {
                'tables': {},
                'indexes': {},
                'performance': {},
                'recommendations': []
            }
            
            # 1. 分析表大小和行数
            self.cursor.execute("""
                SELECT 
                    schemaname,
                    relname as tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname || '.' || relname)) as total_size,
                    pg_size_pretty(pg_relation_size(schemaname || '.' || relname)) as table_size,
                    pg_size_pretty(pg_total_relation_size(schemaname || '.' || relname) - 
                                  pg_relation_size(schemaname || '.' || relname)) as index_size,
                    n_live_tup as row_count,
                    n_dead_tup as dead_rows
                FROM pg_stat_user_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname || '.' || relname) DESC
            """)
            
            tables = self.cursor.fetchall()
            for table in tables:
                schemaname, tablename, total_size, table_size, index_size, row_count, dead_rows = table
                health_report['tables'][tablename] = {
                    'total_size': total_size,
                    'table_size': table_size,
                    'index_size': index_size,
                    'row_count': row_count,
                    'dead_rows': dead_rows,
                    'dead_row_percentage': (dead_rows / row_count * 100) if row_count > 0 else 0
                }
            
            # 2. 分析索引使用情况
            self.cursor.execute("""
                SELECT 
                    schemaname,
                    relname as tablename,
                    indexrelname,
                    pg_size_pretty(pg_relation_size(schemaname || '.' || indexrelname)) as index_size,
                    idx_scan as index_scans,
                    idx_tup_read as tuples_read,
                    idx_tup_fetch as tuples_fetched
                FROM pg_stat_user_indexes
                WHERE schemaname = 'public'
                ORDER BY pg_relation_size(schemaname || '.' || indexrelname) DESC
            """)
            
            indexes = self.cursor.fetchall()
            for index in indexes:
                schemaname, tablename, indexname, index_size, index_scans, tuples_read, tuples_fetched = index
                health_report['indexes'][indexname] = {
                    'table': tablename,
                    'size': index_size,
                    'scans': index_scans,
                    'tuples_read': tuples_read,
                    'tuples_fetched': tuples_fetched,
                    'efficiency': (tuples_fetched / tuples_read * 100) if tuples_read > 0 else 0
                }
            
            # 3. 分析查询性能
            try:
                self.cursor.execute("""
                    SELECT 
                        query,
                        calls,
                        total_time,
                        mean_time,
                        rows,
                        shared_blks_hit,
                        shared_blks_read
                    FROM pg_stat_statements
                    ORDER BY total_time DESC
                    LIMIT 10
                """)
                
                slow_queries = self.cursor.fetchall()
                health_report['performance']['slow_queries'] = slow_queries
            except Exception as e:
                logger.warning(f"无法获取慢查询统计: {e}")
                logger.warning("请启用pg_stat_statements扩展: CREATE EXTENSION IF NOT EXISTS pg_stat_statements;")
                health_report['performance']['slow_queries'] = []
            
            # 4. 生成优化建议
            self.generate_recommendations(health_report)
            
            return health_report
            
        except Exception as e:
            logger.error(f"❌ 分析数据库健康状况失败: {e}")
            return {}
    
    def generate_recommendations(self, health_report: Dict):
        """生成优化建议"""
        recommendations = []
        
        # 检查死行
        for table_name, table_info in health_report.get('tables', {}).items():
            dead_row_percentage = table_info.get('dead_row_percentage', 0)
            if dead_row_percentage > 10:  # 死行超过10%
                recommendations.append({
                    'type': 'VACUUM',
                    'table': table_name,
                    'reason': f"表 '{table_name}' 有 {dead_row_percentage:.1f}% 的死行，建议执行 VACUUM",
                    'command': f"VACUUM ANALYZE {table_name};"
                })
        
        # 检查未使用的索引
        for index_name, index_info in health_report.get('indexes', {}).items():
            index_scans = index_info.get('scans', 0)
            if index_scans == 0:  # 从未使用过的索引
                recommendations.append({
                    'type': 'INDEX',
                    'index': index_name,
                    'table': index_info.get('table'),
                    'reason': f"索引 '{index_name}' 从未被使用过，考虑删除",
                    'command': f"DROP INDEX IF EXISTS {index_name};"
                })
        
        # 检查低效索引
        for index_name, index_info in health_report.get('indexes', {}).items():
            efficiency = index_info.get('efficiency', 0)
            if 0 < efficiency < 10:  # 效率低于10%
                recommendations.append({
                    'type': 'INDEX',
                    'index': index_name,
                    'table': index_info.get('table'),
                    'reason': f"索引 '{index_name}' 效率较低 ({efficiency:.1f}%)，可能需要重新设计",
                    'command': f"REINDEX INDEX {index_name};"
                })
        
        # 检查大表
        for table_name, table_info in health_report.get('tables', {}).items():
            total_size = table_info.get('total_size', '0 MB')
            # 提取数字部分
            size_value = float(total_size.split()[0])
            size_unit = total_size.split()[1]
            
            if size_unit == 'GB' and size_value > 1:  # 大于1GB的表
                recommendations.append({
                    'type': 'PARTITION',
                    'table': table_name,
                    'reason': f"表 '{table_name}' 较大 ({total_size})，考虑分区",
                    'command': f"-- 考虑按 release_date 分区\n-- ALTER TABLE {table_name} ADD PARTITION ..."
                })
        
        health_report['recommendations'] = recommendations
    
    def execute_vacuum(self, table_name: Optional[str] = None) -> bool:
        """执行VACUUM操作"""
        try:
            if table_name:
                logger.info(f"执行 VACUUM ANALYZE {table_name}...")
                self.cursor.execute(f"VACUUM ANALYZE {table_name};")
            else:
                logger.info("执行 VACUUM ANALYZE 所有表...")
                self.cursor.execute("VACUUM ANALYZE;")
            
            self.conn.commit()
            logger.info("✅ VACUUM 操作完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ VACUUM 操作失败: {e}")
            self.conn.rollback()
            return False
    
    def reindex_table(self, table_name: str) -> bool:
        """重建表索引"""
        try:
            logger.info(f"重建表 '{table_name}' 的索引...")
            self.cursor.execute(f"REINDEX TABLE {table_name};")
            self.conn.commit()
            logger.info(f"✅ 表 '{table_name}' 索引重建完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 重建索引失败: {e}")
            self.conn.rollback()
            return False
    
    def update_statistics(self) -> bool:
        """更新数据库统计信息"""
        try:
            logger.info("更新数据库统计信息...")
            self.cursor.execute("ANALYZE;")
            self.conn.commit()
            logger.info("✅ 统计信息更新完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新统计信息失败: {e}")
            self.conn.rollback()
            return False
    
    def create_missing_indexes(self) -> bool:
        """创建缺失的索引"""
        try:
            logger.info("检查并创建缺失的索引...")
            
            # 检查movies表的外键索引
            missing_indexes = [
                # movies表
                "CREATE INDEX IF NOT EXISTS idx_movies_original_language ON movies(original_language);",
                "CREATE INDEX IF NOT EXISTS idx_movies_status ON movies(status);",
                
                # 复合索引
                "CREATE INDEX IF NOT EXISTS idx_movies_genre_popularity ON movies USING gin(genres) WHERE popularity > 5;",
                "CREATE INDEX IF NOT EXISTS idx_movies_date_vote ON movies(release_date, vote_average);",
                
                # 部分索引
                "CREATE INDEX IF NOT EXISTS idx_movies_high_rated ON movies(vote_average) WHERE vote_average > 7.5;",
                "CREATE INDEX IF NOT EXISTS idx_movies_high_revenue ON movies(revenue) WHERE revenue > 100000000;",
                
                # 用户相关表
                "CREATE INDEX IF NOT EXISTS idx_user_ratings_created ON user_ratings(created_at);",
                "CREATE INDEX IF NOT EXISTS idx_user_watch_history_date ON user_watch_history(watch_date);"
            ]
            
            created_count = 0
            for sql in missing_indexes:
                try:
                    self.cursor.execute(sql)
                    created_count += 1
                except Exception as e:
                    logger.warning(f"创建索引时出现警告: {e}")
            
            self.conn.commit()
            logger.info(f"✅ 创建了 {created_count} 个新索引")
            return True
            
        except Exception as e:
            logger.error(f"❌ 创建索引失败: {e}")
            self.conn.rollback()
            return False
    
    def optimize_query_performance(self) -> bool:
        """优化查询性能"""
        try:
            logger.info("优化查询性能...")
            
            # 1. 设置work_mem（针对复杂排序和哈希操作）
            self.cursor.execute("SHOW work_mem;")
            current_work_mem = self.cursor.fetchone()[0]
            logger.info(f"当前 work_mem: {current_work_mem}")
            
            # 2. 检查shared_buffers
            self.cursor.execute("SHOW shared_buffers;")
            current_shared_buffers = self.cursor.fetchone()[0]
            logger.info(f"当前 shared_buffers: {current_shared_buffers}")
            
            # 3. 建议的配置优化
            recommendations = [
                {
                    'parameter': 'work_mem',
                    'current': current_work_mem,
                    'recommended': '16MB',
                    'reason': '提高复杂查询的排序和哈希操作性能'
                },
                {
                    'parameter': 'shared_buffers',
                    'current': current_shared_buffers,
                    'recommended': '25% of RAM',
                    'reason': '提高数据缓存效率'
                },
                {
                    'parameter': 'effective_cache_size',
                    'current': '?',
                    'recommended': '75% of RAM',
                    'reason': '帮助查询规划器做出更好的索引选择'
                },
                {
                    'parameter': 'maintenance_work_mem',
                    'current': '?',
                    'recommended': '64MB',
                    'reason': '提高VACUUM和CREATE INDEX性能'
                }
            ]
            
            logger.info("查询性能优化建议:")
            for rec in recommendations:
                logger.info(f"  🔧 {rec['parameter']}: {rec['current']} → {rec['recommended']}")
                logger.info(f"     原因: {rec['reason']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 优化查询性能失败: {e}")
            return False
    
    def generate_optimization_report(self, health_report: Dict):
        """生成优化报告"""
        print("=" * 80)
        print("数据库优化报告")
        print("=" * 80)
        
        # 表统计
        print("\n📊 表统计:")
        print("-" * 40)
        for table_name, table_info in health_report.get('tables', {}).items():
            print(f"{table_name}:")
            print(f"  行数: {table_info['row_count']:,}")
            print(f"  总大小: {table_info['total_size']} (表: {table_info['table_size']}, 索引: {table_info['index_size']})")
            if table_info['dead_row_percentage'] > 5:
                print(f"  ⚠️  死行: {table_info['dead_rows']:,} ({table_info['dead_row_percentage']:.1f}%)")
            print()
        
        # 索引统计
        print("\n🔍 索引统计:")
        print("-" * 40)
        unused_indices = []
        for index_name, index_info in health_report.get('indexes', {}).items():
            if index_info['scans'] == 0:
                unused_indices.append((index_name, index_info['table']))
            else:
                print(f"{index_name} ({index_info['table']}):")
                print(f"  大小: {index_info['size']}")
                print(f"  扫描次数: {index_info['scans']:,}")
                print(f"  效率: {index_info['efficiency']:.1f}%")
                print()
        
        if unused_indices:
            print("\n⚠️  未使用的索引:")
            for index_name, table_name in unused_indices:
                print(f"  {index_name} (表: {table_name})")
        
        # 优化建议
        print("\n💡 优化建议:")
        print("-" * 40)
        recommendations = health_report.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. [{rec['type']}] {rec['reason']}")
                print(f"   命令: {rec['command']}")
                print()
        else:
            print("✅ 数据库状态良好，无需优化")
        
        # 慢查询
        print("\n🐌 最慢的查询:")
        print("-" * 40)
        slow_queries = health_report.get('performance', {}).get('slow_queries', [])
        if slow_queries:
            for i, query in enumerate(slow_queries[:5], 1):
                query_text, calls, total_time, mean_time, rows, shared_blks_hit, shared_blks_read = query
                print(f"{i}. 平均时间: {mean_time:.2f}ms, 调用次数: {calls}")
                print(f"   总时间: {total_time:.2f}ms, 返回行数: {rows}")
                # 简化查询文本
                short_query = query_text[:100] + "..." if len(query_text) > 100 else query_text
                print(f"   查询: {short_query}")
                print()
        else:
            print("✅ 没有发现慢查询")
        
        print("=" * 80)
    
    def run_optimization(self, execute: bool = False):
        """运行优化流程"""
        print("=" * 80)
        print("数据库优化工具")
        print("=" * 80)
        
        if not self.connect():
            print("数据库连接失败")
            return
        
        try:
            # 1. 分析数据库健康状况
            print("\n1. 分析数据库健康状况...")
            health_report = self.analyze_database_health()
            
            # 2. 生成优化报告
            print("\n2. 生成优化报告...")
            self.generate_optimization_report(health_report)
            
            if execute:
                print("\n3. 执行优化操作...")
                
                # 执行VACUUM
                print("  执行 VACUUM ANALYZE...")
                self.execute_vacuum()
                
                # 更新统计信息
                print("  更新统计信息...")
                self.update_statistics()
                
                # 创建缺失索引
                print("  创建缺失索引...")
                self.create_missing_indexes()
                
                # 优化查询性能
                print("  优化查询性能...")
                self.optimize_query_performance()
                
                print("\n✅ 所有优化操作完成")
            else:
                print("\n📋 优化建议已生成，要执行这些优化，请使用 --execute 参数")
            
        finally:
            self.disconnect()
        
        print("=" * 80)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库优化工具')
    parser.add_argument('--execute', action='store_true', help='执行优化操作')
    parser.add_argument('--password', default='356921', help='数据库密码')
    
    args = parser.parse_args()
    
    optimizer = DatabaseOptimizer(password=args.password)
    optimizer.run_optimization(execute=args.execute)

if __name__ == "__main__":
    main()
