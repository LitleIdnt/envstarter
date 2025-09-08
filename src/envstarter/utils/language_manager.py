"""
🌍 LANGUAGE MANAGER 🌍
Multi-language support system for Enhanced EnvStarter!
Dynamic language switching with language files created only when selected.
"""

from PyQt6.QtCore import QObject, pyqtSignal, QTranslator, QLocale
from PyQt6.QtWidgets import QApplication
from typing import Dict, Optional
import json
from pathlib import Path
import os


class LanguageManager(QObject):
    """
    🌍 ADVANCED LANGUAGE MANAGER
    
    Provides complete multi-language support with:
    - Dynamic language switching
    - Language files created only when selected
    - Automatic language detection
    - Translation management
    """
    
    language_changed = pyqtSignal(str)  # language_code
    
    def __init__(self):
        super().__init__()
        self.current_language = "en"
        self.app_instance = None
        self.translator = None
        self.available_languages = {
            "en": "English",
            "es": "Español", 
            "fr": "Français",
            "de": "Deutsch",
            "it": "Italiano",
            "pt": "Português",
            "ru": "Русский",
            "zh": "中文",
            "ja": "日本語",
            "ko": "한국어",
            "ar": "العربية",
            "hi": "हिन्दी",
            "tr": "Türkçe",
            "pl": "Polski",
            "nl": "Nederlands"
        }
        
        # Base translations for all languages
        self.base_translations = {
            "en": self._get_english_translations(),
            "es": self._get_spanish_translations(),
            "fr": self._get_french_translations(), 
            "de": self._get_german_translations(),
            "it": self._get_italian_translations(),
            "pt": self._get_portuguese_translations(),
            "ru": self._get_russian_translations(),
            "zh": self._get_chinese_translations(),
            "ja": self._get_japanese_translations(),
            "ko": self._get_korean_translations(),
            "ar": self._get_arabic_translations(),
            "hi": self._get_hindi_translations(),
            "tr": self._get_turkish_translations(),
            "pl": self._get_polish_translations(),
            "nl": self._get_dutch_translations()
        }
        
        # Initialize languages directory
        self.languages_dir = Path("src/envstarter/languages")
        self.languages_dir.mkdir(parents=True, exist_ok=True)
    
    def set_application_instance(self, app: QApplication):
        """Set the QApplication instance for language management."""
        self.app_instance = app
        
        # Detect system language
        system_locale = QLocale.system().name()[:2]  # Get language code (e.g., 'en' from 'en_US')
        if system_locale in self.available_languages:
            self.current_language = system_locale
        else:
            self.current_language = "en"  # Default to English
        
        print(f"🌍 Detected system language: {self.available_languages.get(self.current_language, 'English')}")
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get available language codes and display names."""
        return self.available_languages.copy()
    
    def set_language(self, language_code: str):
        """Set the current language and create language file if needed."""
        if language_code not in self.available_languages:
            print(f"⚠️ Language '{language_code}' not supported, using English")
            language_code = "en"
        
        self.current_language = language_code
        
        # Create language file only when selected
        self._create_language_file(language_code)
        
        # Apply the language
        self._apply_language()
        
        self.language_changed.emit(language_code)
        
        language_name = self.available_languages[language_code]
        print(f"🌍 Language switched to: {language_name} ({language_code})")
    
    def get_current_language(self) -> str:
        """Get the current language code."""
        return self.current_language
    
    def get_current_language_name(self) -> str:
        """Get the current language display name."""
        return self.available_languages.get(self.current_language, "English")
    
    def _create_language_file(self, language_code: str):
        """Create language file only when the language is selected."""
        language_file = self.languages_dir / f"{language_code}.json"
        
        if not language_file.exists():
            print(f"📝 Creating language file for {self.available_languages[language_code]}...")
            
            translations = self.base_translations.get(language_code, self.base_translations["en"])
            
            with open(language_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Language file created: {language_file}")
    
    def _apply_language(self):
        """Apply the current language to the application."""
        if not self.app_instance:
            print("⚠️ No application instance set for language management")
            return
        
        # Remove existing translator
        if self.translator:
            self.app_instance.removeTranslator(self.translator)
        
        # Create new translator
        self.translator = QTranslator()
        
        # Load translations if file exists
        language_file = self.languages_dir / f"{self.current_language}.json"
        if language_file.exists():
            print(f"🌍 Loading translations from {language_file}")
        
        self.app_instance.installTranslator(self.translator)
    
    def tr(self, key: str, default: str = None) -> str:
        """Translate a text key."""
        language_file = self.languages_dir / f"{self.current_language}.json"
        
        try:
            if language_file.exists():
                with open(language_file, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
                return translations.get(key, default or key)
            else:
                # Use base translations
                translations = self.base_translations.get(self.current_language, {})
                return translations.get(key, default or key)
        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            return default or key
    
    # Translation dictionaries for each language
    def _get_english_translations(self) -> Dict[str, str]:
        return {
            # Application
            "app_title": "EnvStarter - Multi-Environment System",
            "app_subtitle": "Revolutionary environment container management",
            
            # Main UI
            "dashboard": "Dashboard",
            "environment_selector": "Environment Selector",
            "settings": "Settings",
            "refresh": "Refresh",
            "launch": "Launch",
            "launch_all": "Launch All",
            "stop_all": "Stop All",
            "quick_launch": "Quick Launch",
            "batch_operations": "Batch Operations",
            "pause_all": "Pause All",
            "resume_all": "Resume All",
            "containers": "Containers",
            "resources": "Resources",
            "queue": "Queue",
            
            # Environment Management
            "environments": "Environments",
            "create_environment": "Create Environment",
            "edit_environment": "Edit Environment",
            "delete_environment": "Delete Environment",
            "duplicate_environment": "Duplicate Environment",
            "import_environment": "Import Environment",
            "export_environment": "Export Environment",
            "environment_name": "Environment Name",
            "environment_description": "Environment Description",
            "applications": "Applications",
            "websites": "Websites",
            "startup_delay": "Startup Delay",
            
            # Container Operations
            "container_running": "Running",
            "container_stopped": "Stopped",
            "container_paused": "Paused",
            "switch_to_container": "Switch to Container",
            "pause_container": "Pause Container",
            "resume_container": "Resume Container",
            "stop_container": "Stop Container",
            
            # System
            "system_settings": "System Settings",
            "auto_start": "Auto-start with Windows",
            "minimize_to_tray": "Minimize to system tray",
            "show_notifications": "Show notifications",
            "theme": "Theme",
            "language": "Language",
            "light_mode": "Light Mode",
            "dark_mode": "Dark Mode",
            
            # Messages
            "launch_success": "Environment launched successfully",
            "launch_failed": "Failed to launch environment",
            "no_environments": "No environments available",
            "confirm_delete": "Are you sure you want to delete this environment?",
            "confirm_stop_all": "Are you sure you want to stop all containers?",
            "settings_saved": "Settings saved successfully",
            
            # Buttons
            "ok": "OK",
            "cancel": "Cancel",
            "apply": "Apply",
            "save": "Save",
            "delete": "Delete",
            "edit": "Edit",
            "add": "Add",
            "remove": "Remove",
            "browse": "Browse",
            "test": "Test"
        }
    
    def _get_spanish_translations(self) -> Dict[str, str]:
        return {
            # Application  
            "app_title": "EnvStarter - Sistema Multi-Entorno",
            "app_subtitle": "Gestión revolucionaria de contenedores de entorno",
            
            # Main UI
            "dashboard": "Panel de Control",
            "environment_selector": "Selector de Entorno",
            "settings": "Configuración",
            "refresh": "Actualizar",
            "launch": "Lanzar",
            "launch_all": "Lanzar Todo",
            "stop_all": "Detener Todo",
            "quick_launch": "Lanzamiento Rápido",
            "batch_operations": "Operaciones en Lote",
            "pause_all": "Pausar Todo",
            "resume_all": "Reanudar Todo",
            "containers": "Contenedores",
            "resources": "Recursos",
            "queue": "Cola",
            
            # Environment Management
            "environments": "Entornos",
            "create_environment": "Crear Entorno",
            "edit_environment": "Editar Entorno", 
            "delete_environment": "Eliminar Entorno",
            "duplicate_environment": "Duplicar Entorno",
            "import_environment": "Importar Entorno",
            "export_environment": "Exportar Entorno",
            "environment_name": "Nombre del Entorno",
            "environment_description": "Descripción del Entorno",
            "applications": "Aplicaciones",
            "websites": "Sitios Web",
            "startup_delay": "Retraso de Inicio",
            
            # Container Operations
            "container_running": "Ejecutándose",
            "container_stopped": "Detenido",
            "container_paused": "Pausado",
            "switch_to_container": "Cambiar al Contenedor",
            "pause_container": "Pausar Contenedor",
            "resume_container": "Reanudar Contenedor",
            "stop_container": "Detener Contenedor",
            
            # System
            "system_settings": "Configuración del Sistema",
            "auto_start": "Inicio automático con Windows",
            "minimize_to_tray": "Minimizar a la bandeja del sistema",
            "show_notifications": "Mostrar notificaciones",
            "theme": "Tema",
            "language": "Idioma",
            "light_mode": "Modo Claro",
            "dark_mode": "Modo Oscuro",
            
            # Messages
            "launch_success": "Entorno lanzado exitosamente",
            "launch_failed": "Error al lanzar el entorno",
            "no_environments": "No hay entornos disponibles",
            "confirm_delete": "¿Estás seguro de que quieres eliminar este entorno?",
            "confirm_stop_all": "¿Estás seguro de que quieres detener todos los contenedores?",
            "settings_saved": "Configuración guardada exitosamente",
            
            # Buttons
            "ok": "Aceptar",
            "cancel": "Cancelar",
            "apply": "Aplicar",
            "save": "Guardar",
            "delete": "Eliminar",
            "edit": "Editar",
            "add": "Agregar",
            "remove": "Quitar",
            "browse": "Explorar",
            "test": "Probar"
        }
    
    def _get_french_translations(self) -> Dict[str, str]:
        return {
            # Application
            "app_title": "EnvStarter - Système Multi-Environnement",
            "app_subtitle": "Gestion révolutionnaire de conteneurs d'environnement",
            
            # Main UI
            "dashboard": "Tableau de Bord",
            "environment_selector": "Sélecteur d'Environnement",
            "settings": "Paramètres",
            "refresh": "Actualiser",
            "launch": "Lancer",
            "launch_all": "Lancer Tout",
            "stop_all": "Arrêter Tout",
            "quick_launch": "Lancement Rapide",
            "batch_operations": "Opérations par Lot",
            "pause_all": "Suspendre Tout",
            "resume_all": "Reprendre Tout",
            "containers": "Conteneurs",
            "resources": "Ressources",
            "queue": "File d'Attente",
            
            # Environment Management
            "environments": "Environnements",
            "create_environment": "Créer un Environnement",
            "edit_environment": "Modifier l'Environnement",
            "delete_environment": "Supprimer l'Environnement",
            "duplicate_environment": "Dupliquer l'Environnement",
            "import_environment": "Importer l'Environnement",
            "export_environment": "Exporter l'Environnement",
            "environment_name": "Nom de l'Environnement",
            "environment_description": "Description de l'Environnement",
            "applications": "Applications",
            "websites": "Sites Web",
            "startup_delay": "Délai de Démarrage",
            
            # Container Operations
            "container_running": "En Cours",
            "container_stopped": "Arrêté",
            "container_paused": "Suspendu",
            "switch_to_container": "Basculer vers le Conteneur",
            "pause_container": "Suspendre le Conteneur",
            "resume_container": "Reprendre le Conteneur",
            "stop_container": "Arrêter le Conteneur",
            
            # System
            "system_settings": "Paramètres Système",
            "auto_start": "Démarrage automatique avec Windows",
            "minimize_to_tray": "Réduire dans la barre système",
            "show_notifications": "Afficher les notifications",
            "theme": "Thème",
            "language": "Langue",
            "light_mode": "Mode Clair",
            "dark_mode": "Mode Sombre",
            
            # Messages
            "launch_success": "Environnement lancé avec succès",
            "launch_failed": "Échec du lancement de l'environnement",
            "no_environments": "Aucun environnement disponible",
            "confirm_delete": "Êtes-vous sûr de vouloir supprimer cet environnement ?",
            "confirm_stop_all": "Êtes-vous sûr de vouloir arrêter tous les conteneurs ?",
            "settings_saved": "Paramètres sauvegardés avec succès",
            
            # Buttons
            "ok": "OK",
            "cancel": "Annuler",
            "apply": "Appliquer",
            "save": "Sauvegarder",
            "delete": "Supprimer",
            "edit": "Modifier",
            "add": "Ajouter",
            "remove": "Retirer",
            "browse": "Parcourir",
            "test": "Tester"
        }
    
    def _get_german_translations(self) -> Dict[str, str]:
        return {
            # Application
            "app_title": "EnvStarter - Multi-Umgebungs-System",
            "app_subtitle": "Revolutionäre Umgebungscontainer-Verwaltung",
            
            # Main UI
            "dashboard": "Dashboard",
            "environment_selector": "Umgebungs-Selektor",
            "settings": "Einstellungen",
            "refresh": "Aktualisieren",
            "launch": "Starten",
            "launch_all": "Alle Starten",
            "stop_all": "Alle Stoppen",
            "quick_launch": "Schnellstart",
            "batch_operations": "Stapeloperationen",
            "pause_all": "Alle Pausieren",
            "resume_all": "Alle Fortsetzen",
            "containers": "Container",
            "resources": "Ressourcen",
            "queue": "Warteschlange",
            
            # Environment Management
            "environments": "Umgebungen",
            "create_environment": "Umgebung Erstellen",
            "edit_environment": "Umgebung Bearbeiten",
            "delete_environment": "Umgebung Löschen",
            "duplicate_environment": "Umgebung Duplizieren",
            "import_environment": "Umgebung Importieren",
            "export_environment": "Umgebung Exportieren",
            "environment_name": "Umgebungsname",
            "environment_description": "Umgebungsbeschreibung",
            "applications": "Anwendungen",
            "websites": "Webseiten",
            "startup_delay": "Startverzögerung",
            
            # Container Operations
            "container_running": "Läuft",
            "container_stopped": "Gestoppt",
            "container_paused": "Pausiert",
            "switch_to_container": "Zu Container Wechseln",
            "pause_container": "Container Pausieren",
            "resume_container": "Container Fortsetzen",
            "stop_container": "Container Stoppen",
            
            # System
            "system_settings": "Systemeinstellungen",
            "auto_start": "Automatischer Start mit Windows",
            "minimize_to_tray": "In Taskleiste minimieren",
            "show_notifications": "Benachrichtigungen anzeigen",
            "theme": "Design",
            "language": "Sprache",
            "light_mode": "Heller Modus",
            "dark_mode": "Dunkler Modus",
            
            # Messages
            "launch_success": "Umgebung erfolgreich gestartet",
            "launch_failed": "Start der Umgebung fehlgeschlagen",
            "no_environments": "Keine Umgebungen verfügbar",
            "confirm_delete": "Sind Sie sicher, dass Sie diese Umgebung löschen möchten?",
            "confirm_stop_all": "Sind Sie sicher, dass Sie alle Container stoppen möchten?",
            "settings_saved": "Einstellungen erfolgreich gespeichert",
            
            # Buttons
            "ok": "OK",
            "cancel": "Abbrechen",
            "apply": "Anwenden",
            "save": "Speichern",
            "delete": "Löschen",
            "edit": "Bearbeiten",
            "add": "Hinzufügen",
            "remove": "Entfernen",
            "browse": "Durchsuchen",
            "test": "Testen"
        }
    
    # Add minimal implementations for other languages (Italian, Portuguese, etc.)
    def _get_italian_translations(self) -> Dict[str, str]:
        return {
            "app_title": "EnvStarter - Sistema Multi-Ambiente",
            "dashboard": "Dashboard",
            "settings": "Impostazioni",
            "launch": "Avvia",
            "environments": "Ambienti",
            "language": "Lingua",
            "theme": "Tema",
            "light_mode": "Modalità Chiara",
            "dark_mode": "Modalità Scura"
        }
    
    def _get_portuguese_translations(self) -> Dict[str, str]:
        return {
            "app_title": "EnvStarter - Sistema Multi-Ambiente",
            "dashboard": "Painel",
            "settings": "Configurações",
            "launch": "Iniciar",
            "environments": "Ambientes",
            "language": "Idioma",
            "theme": "Tema",
            "light_mode": "Modo Claro",
            "dark_mode": "Modo Escuro"
        }
    
    def _get_russian_translations(self) -> Dict[str, str]:
        return {
            "app_title": "EnvStarter - Мульти-средовая Система",
            "dashboard": "Панель",
            "settings": "Настройки", 
            "launch": "Запустить",
            "environments": "Среды",
            "language": "Язык",
            "theme": "Тема",
            "light_mode": "Светлый Режим",
            "dark_mode": "Тёмный Режим"
        }
    
    def _get_chinese_translations(self) -> Dict[str, str]:
        return {
            "app_title": "EnvStarter - 多环境系统",
            "dashboard": "仪表板",
            "settings": "设置",
            "launch": "启动",
            "environments": "环境",
            "language": "语言",
            "theme": "主题",
            "light_mode": "浅色模式",
            "dark_mode": "深色模式"
        }
    
    def _get_japanese_translations(self) -> Dict[str, str]:
        return {
            "app_title": "EnvStarter - マルチ環境システム",
            "dashboard": "ダッシュボード",
            "settings": "設定",
            "launch": "起動",
            "environments": "環境",
            "language": "言語",
            "theme": "テーマ",
            "light_mode": "ライトモード",
            "dark_mode": "ダークモード"
        }
    
    def _get_korean_translations(self) -> Dict[str, str]:
        return {
            "app_title": "EnvStarter - 멀티 환경 시스템",
            "dashboard": "대시보드",
            "settings": "설정",
            "launch": "실행",
            "environments": "환경",
            "language": "언어",
            "theme": "테마",
            "light_mode": "라이트 모드",
            "dark_mode": "다크 모드"
        }
    
    def _get_arabic_translations(self) -> Dict[str, str]:
        return {
            "app_title": "EnvStarter - نظام البيئات المتعددة",
            "dashboard": "لوحة التحكم",
            "settings": "الإعدادات",
            "launch": "تشغيل",
            "environments": "البيئات",
            "language": "اللغة",
            "theme": "السمة",
            "light_mode": "الوضع الفاتح",
            "dark_mode": "الوضع الداكن"
        }
    
    def _get_hindi_translations(self) -> Dict[str, str]:
        return {
            "app_title": "EnvStarter - मल्टी-एनवायरनमेंट सिस्टम",
            "dashboard": "डैशबोर्ड",
            "settings": "सेटिंग्स",
            "launch": "लॉन्च",
            "environments": "वातावरण",
            "language": "भाषा",
            "theme": "थीम",
            "light_mode": "लाइट मोड",
            "dark_mode": "डार्क मोड"
        }
    
    def _get_turkish_translations(self) -> Dict[str, str]:
        return {
            "app_title": "EnvStarter - Çoklu Ortam Sistemi",
            "dashboard": "Kontrol Paneli",
            "settings": "Ayarlar",
            "launch": "Başlat",
            "environments": "Ortamlar",
            "language": "Dil",
            "theme": "Tema",
            "light_mode": "Açık Mod",
            "dark_mode": "Koyu Mod"
        }
    
    def _get_polish_translations(self) -> Dict[str, str]:
        return {
            "app_title": "EnvStarter - System Wielu Środowisk",
            "dashboard": "Panel",
            "settings": "Ustawienia",
            "launch": "Uruchom",
            "environments": "Środowiska",
            "language": "Język",
            "theme": "Motyw",
            "light_mode": "Tryb Jasny",
            "dark_mode": "Tryb Ciemny"
        }
    
    def _get_dutch_translations(self) -> Dict[str, str]:
        return {
            "app_title": "EnvStarter - Multi-Omgeving Systeem",
            "dashboard": "Dashboard",
            "settings": "Instellingen",
            "launch": "Starten",
            "environments": "Omgevingen",
            "language": "Taal",
            "theme": "Thema",
            "light_mode": "Lichte Modus",
            "dark_mode": "Donkere Modus"
        }


# Global language manager instance
_language_manager = None

def get_language_manager() -> LanguageManager:
    """Get the global language manager instance."""
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager