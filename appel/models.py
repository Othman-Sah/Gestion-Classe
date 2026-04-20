from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Filiere(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    salle = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

class Etudiant(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='etudiant_profile')
    nom = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    numero_etudiant = models.CharField(max_length=30, blank=True, null=True, unique=True)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='etudiants')
    total_presences = models.PositiveIntegerField(default=0)
    total_absences = models.PositiveIntegerField(default=0)
    date_inscription = models.DateField(default=now)

    def __str__(self):
        return self.nom

class Presence(models.Model):
    etudiant = models.ForeignKey('Etudiant', on_delete=models.CASCADE, related_name='presences')
    date = models.DateField(default=now)
    present = models.BooleanField()

    class Meta:
        unique_together = ('etudiant', 'date')
        ordering = ['-date', 'etudiant__nom']

    def __str__(self):
        return f"{self.etudiant.nom} - {'Present' if self.present else 'Absent'} le {self.date}"


class AbsenceJustification(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, _('En attente')),
        (STATUS_APPROVED, _('Approuvee')),
        (STATUS_REJECTED, _('Refusee')),
    ]

    presence = models.OneToOneField(Presence, on_delete=models.CASCADE, related_name='justification')
    reason = models.CharField(max_length=150)
    details = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Justification {self.presence.etudiant.nom} - {self.presence.date}"


class ClassSchedule(models.Model):
    """Schedule/Timetable for classes"""
    DAY_CHOICES = [
        ('Monday', _('Lundi')),
        ('Tuesday', _('Mardi')),
        ('Wednesday', _('Mercredi')),
        ('Thursday', _('Jeudi')),
        ('Friday', _('Vendredi')),
        ('Saturday', _('Samedi')),
    ]

    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.CharField(max_length=100, help_text=_("Subject or course name"))
    professor = models.CharField(max_length=100, blank=True)
    room = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ('filiere', 'day_of_week', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.filiere.nom} - {self.day_of_week} {self.start_time}"
