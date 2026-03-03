from django.contrib import admin
from .models import GameConfig, GameLevel, GameContent, GameSession, GameAttempt

# ==========================================
# GAME CONFIGURATION ADMIN
# ==========================================

@admin.register(GameConfig)
class GameConfigAdmin(admin.ModelAdmin):
    list_display = ('title', 'game_type', 'event', 'is_active', 'default_time_limit')
    list_filter = ('game_type', 'is_active', 'event')
    search_fields = ('title', 'game_type')
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'event', 'game_type')
        }),
        ('Configuration', {
            'fields': ('default_time_limit', 'is_active')
        }),
    )


# ==========================================
# GAME LEVEL ADMIN
# ==========================================

@admin.register(GameLevel)
class GameLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'game_config', 'time_limit_seconds', 'max_score', 'difficulty_order')
    list_filter = ('game_config', 'difficulty_order')
    search_fields = ('name', 'game_config__title')
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'game_config')
        }),
        ('Configuration', {
            'fields': ('time_limit_seconds', 'max_score', 'difficulty_order')
        }),
    )


# ==========================================
# GAME CONTENT ADMIN
# ==========================================

@admin.register(GameContent)
class GameContentAdmin(admin.ModelAdmin):
    list_display = ('get_content_preview', 'game_config', 'level', 'content_type', 'points', 'is_active')
    list_filter = ('content_type', 'is_active', 'game_config', 'level')
    search_fields = ('data', 'game_config__title')
    fieldsets = (
        ('Basic Info', {
            'fields': ('game_config', 'level', 'content_type')
        }),
        ('Content', {
            'fields': ('data',)
        }),
        ('Settings', {
            'fields': ('points', 'is_active')
        }),
    )
    
    def get_content_preview(self, obj):
        """Display a preview of the content"""
        if obj.data:
            if isinstance(obj.data, dict) and 'word' in obj.data:
                return obj.data['word']
            elif isinstance(obj.data, str):
                return obj.data[:50]
        return 'N/A'
    get_content_preview.short_description = 'Content Preview'


# ==========================================
# GAME SESSION ADMIN
# ==========================================

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'game_config', 'level', 'event', 'started_at', 'is_active')
    list_filter = ('is_active', 'game_config', 'level', 'event')
    search_fields = ('game_config__title', 'level__name')
    readonly_fields = ('started_at', 'ended_at')
    fieldsets = (
        ('Basic Info', {
            'fields': ('event', 'game_config', 'level')
        }),
        ('Session Control', {
            'fields': ('started_by', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'ended_at'),
            'classes': ('collapse',)
        }),
    )


# ==========================================
# GAME ATTEMPT ADMIN
# ==========================================

@admin.register(GameAttempt)
class GameAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'viewer', 'session', 'score', 'fastest_correct_time', 'time_spent_seconds', 'created_at')
    list_filter = ('session__game_config', 'created_at')
    search_fields = ('viewer__email', 'viewer__full_name', 'session__id')
    readonly_fields = ('created_at', 'raw_answers')
    fieldsets = (
        ('Player Info', {
            'fields': ('session', 'viewer')
        }),
        ('Scoring', {
            'fields': ('score', 'fastest_correct_time', 'time_spent_seconds')
        }),
        ('Details', {
            'fields': ('raw_answers',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent manual addition of game attempts (should be created by game API)"""
        return False
