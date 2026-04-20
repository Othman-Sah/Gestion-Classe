from django.contrib import admin

from .models import AbsenceJustification, ClassSchedule, Etudiant, Filiere, Presence


@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'salle', 'created_at')
    search_fields = ('nom', 'salle')


@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'numero_etudiant', 'filiere', 'user', 'total_presences', 'total_absences')
    list_filter = ('filiere',)
    search_fields = ('nom', 'numero_etudiant', 'email')


@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'etudiant', 'date', 'present')
    list_filter = ('date', 'present', 'etudiant__filiere')


@admin.register(AbsenceJustification)
class AbsenceJustificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'presence', 'reason', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('presence__etudiant__nom', 'reason', 'details')


@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'filiere', 'day_of_week', 'start_time', 'end_time', 'subject', 'professor')
    list_filter = ('filiere', 'day_of_week')
    search_fields = ('subject', 'professor', 'filiere__nom')
    ordering = ('day_of_week', 'start_time')
