from django.conf import settings

DEBUG_TOOLBAR_PANELS = getattr(settings, 'DEBUG_TOOLBAR_PANELS', (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.profiler.ProfilerDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.cache.CacheDebugPanel',
    # 'debug_toolbar.panels.templates.TemplatesDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.http_vars.HttpVarsDebugPanel',
))
