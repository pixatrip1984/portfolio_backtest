# cleanup_archived_files.py
# Script para limpiar archivos archivados del directorio principal

import os

# Archivos que ya están archivados y se pueden eliminar
files_to_remove = [
    "run_elliott_wave_backtest.py",
    "run_elliott_wave_v2_backtest.py", 
    "run_elliott_wave_v2_optimized.py",
    "run_elliott_wave_v2_fixed.py",
    "run_elliott_wave_v2_final.py",
    "run_elliott_wave_v2_ultra_simple.py",
    "debug_elliott_wave.py",
    "debug_trend_detection.py",
    "run_taew_analysis.py",
    "run_taew_analysis_fast.py"
]

def cleanup_archived_files():
    removed_count = 0
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🗑️  Eliminado: {file}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Error eliminando {file}: {e}")
        else:
            print(f"⚠️  No encontrado: {file}")
    
    print(f"\n📊 Eliminados: {removed_count} archivos obsoletos")
    print("✅ Directorio principal limpio - solo V2.5 activo")

if __name__ == "__main__":
    cleanup_archived_files()
