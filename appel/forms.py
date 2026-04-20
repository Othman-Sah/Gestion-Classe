from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import AbsenceJustification, Etudiant, Filiere


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Nom d'utilisateur"),
        widget=forms.TextInput(attrs={'placeholder': _("Entrez votre identifiant")}),
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': _("Entrez votre mot de passe")}),
    )


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label=_("Mot de passe"),
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': _("Creez un mot de passe")}),
    )
    password2 = forms.CharField(
        label=_("Confirmer le mot de passe"),
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': _("Retapez le mot de passe")}),
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': _("Nom d'utilisateur"),
            'email': _("Email"),
        }
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': _("Choisissez un identifiant")}),
            'email': forms.EmailInput(attrs={'placeholder': _("Votre email")}),
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_("Ce nom d'utilisateur existe deja."))
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', _("Les mots de passe ne correspondent pas."))

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class FiliereForm(forms.ModelForm):
    class Meta:
        model = Filiere
        fields = ['nom', 'salle', 'description']
        labels = {
            'nom': _('Nom de la classe'),
            'salle': _('Salle'),
            'description': _('Description'),
        }
        widgets = {
            'nom': forms.TextInput(attrs={'placeholder': _('Ex: Informatique 2A')}),
            'salle': forms.TextInput(attrs={'placeholder': _('Ex: B12')}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': _('Quelques details sur la classe')}),
        }


class EtudiantForm(forms.ModelForm):
    create_student_account = forms.BooleanField(
        required=False,
        label=_("Creer un compte etudiant"),
    )
    student_username = forms.CharField(
        required=False,
        label=_("Identifiant etudiant"),
        widget=forms.TextInput(attrs={'placeholder': _('Ex: aya.bennani')}),
    )
    student_password = forms.CharField(
        required=False,
        label=_("Mot de passe etudiant"),
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': _('Ex: etu12345')}),
    )

    class Meta:
        model = Etudiant
        fields = ['nom', 'numero_etudiant', 'email']
        labels = {
            'nom': _("Nom complet"),
            'numero_etudiant': _("Numero etudiant"),
            'email': _("Email"),
        }
        widgets = {
            'nom': forms.TextInput(attrs={'placeholder': _('Ex: Salma El Idrissi')}),
            'numero_etudiant': forms.TextInput(attrs={'placeholder': _('Ex: STI-2026-014')}),
            'email': forms.EmailInput(attrs={'placeholder': _('Ex: etudiant@ecole.ma')}),
        }

    def clean(self):
        cleaned_data = super().clean()
        create_student_account = cleaned_data.get('create_student_account')
        username = cleaned_data.get('student_username')
        password = cleaned_data.get('student_password')

        if create_student_account:
            if not username:
                self.add_error('student_username', _("Entrez un identifiant pour l'etudiant."))
            elif User.objects.filter(username=username).exists():
                self.add_error('student_username', _("Cet identifiant existe deja."))

            if not password:
                self.add_error('student_password', _("Entrez un mot de passe pour l'etudiant."))

        return cleaned_data


class AbsenceJustificationForm(forms.ModelForm):
    class Meta:
        model = AbsenceJustification
        fields = ['reason', 'details']
        labels = {
            'reason': _("Motif"),
            'details': _("Explication"),
        }
        widgets = {
            'reason': forms.TextInput(attrs={'placeholder': _('Ex: Rendez-vous medical')}),
            'details': forms.Textarea(attrs={'rows': 4, 'placeholder': _("Ajoutez plus de details sur l'absence")}),
        }


class ImportExcelForm(forms.Form):
    """Form pour importer une liste d'etudiants depuis un fichier Excel"""
    excel_file = forms.FileField(
        label=_("Fichier Excel"),
        help_text=_("Formats acceptes: .xlsx, .xls"),
        widget=forms.FileInput(attrs={'accept': '.xlsx,.xls'}),
    )
    
    def clean_excel_file(self):
        file = self.cleaned_data.get('excel_file')
        if file:
            # Verification de l'extension
            if not (file.name.endswith('.xlsx') or file.name.endswith('.xls')):
                raise forms.ValidationError(_("Veuillez uploader un fichier Excel (.xlsx ou .xls)"))
            # Verification de la taille (max 5MB)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_("Le fichier ne doit pas depasser 5 MB"))
        return file


class PasswordChangeForm(forms.Form):
    """Form for changing user password"""
    current_password = forms.CharField(
        label=_("Mot de passe actuel"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': _("Entrez votre mot de passe actuel"),
            'class': 'form-control'
        }),
    )
    new_password1 = forms.CharField(
        label=_("Nouveau mot de passe"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': _("Entrez votre nouveau mot de passe"),
            'class': 'form-control'
        }),
    )
    new_password2 = forms.CharField(
        label=_("Confirmez le nouveau mot de passe"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': _("Confirmez votre nouveau mot de passe"),
            'class': 'form-control'
        }),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError(_("Le mot de passe actuel est incorrect."))
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError(_("Les nouveaux mots de passe ne correspondent pas."))
            if len(new_password1) < 6:
                raise forms.ValidationError(_("Le nouveau mot de passe doit contenir au moins 6 caracteres."))

        return cleaned_data


class UserProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile information"""
    first_name = forms.CharField(
        label=_("Prénom"),
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _("Votre prénom"),
            'class': 'form-control'
        }),
    )
    last_name = forms.CharField(
        label=_("Nom de famille"),
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _("Votre nom de famille"),
            'class': 'form-control'
        }),
    )
    email = forms.EmailField(
        label=_("Email"),
        required=False,
        widget=forms.EmailInput(attrs={
            'placeholder': _("Votre adresse email"),
            'class': 'form-control'
        }),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_("Cet email est déjà utilisé par un autre compte."))
        return email
