from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from datetime import timedelta, time
from django.utils.timezone import now

from django.core.files.uploadedfile import SimpleUploadedFile

from .forms import ImportExcelForm
from .models import AbsenceJustification, ClassSchedule, Etudiant, Filiere, Presence


class ClassroomFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='prof', password='securepass123')

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_logged_user_can_create_class(self):
        self.client.login(username='prof', password='securepass123')
        response = self.client.post(
            reverse('dashboard'),
            {
                'nom': 'Informatique 1',
                'salle': 'B12',
                'description': 'Classe de premiere annee',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Filiere.objects.filter(nom='Informatique 1').exists())

    def test_logged_user_can_add_student_to_class(self):
        self.client.login(username='prof', password='securepass123')
        filiere = Filiere.objects.create(nom='Maths')
        response = self.client.post(
            reverse('class_detail', args=[filiere.id]),
            {
                'action': 'add_student',
                'nom': 'Aya Bennani',
                'numero_etudiant': 'MAT-001',
                'email': 'aya@example.com',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Etudiant.objects.filter(nom='Aya Bennani', filiere=filiere).exists())

    def test_attendance_updates_student_totals(self):
        self.client.login(username='prof', password='securepass123')
        filiere = Filiere.objects.create(nom='Sciences')
        student = Etudiant.objects.create(nom='Youssef', filiere=filiere)

        response = self.client.post(reverse('save_attendance', args=[filiere.id]), {f'present_{student.id}': 'on'})

        self.assertEqual(response.status_code, 200)
        student.refresh_from_db()
        self.assertEqual(student.total_presences, 1)
        self.assertEqual(student.total_absences, 0)
        self.assertTrue(Presence.objects.filter(etudiant=student, present=True).exists())

    def test_user_can_create_account_from_signup_page(self):
        response = self.client.post(
            reverse('signup'),
            {
                'username': 'newteacher',
                'email': 'teacher@example.com',
                'password1': 'StrongPass123',
                'password2': 'StrongPass123',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newteacher').exists())

    def test_student_account_is_created_when_requested(self):
        self.client.login(username='prof', password='securepass123')
        filiere = Filiere.objects.create(nom='Gestion')

        response = self.client.post(
            reverse('class_detail', args=[filiere.id]),
            {
                'action': 'add_student',
                'nom': 'Lina',
                'numero_etudiant': 'GST-001',
                'email': 'lina@example.com',
                'create_student_account': 'on',
                'student_username': 'lina.student',
                'student_password': 'studentpass123',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        student = Etudiant.objects.get(numero_etudiant='GST-001')
        self.assertIsNotNone(student.user)
        self.assertEqual(student.user.username, 'lina.student')

    def test_student_is_redirected_to_student_dashboard_after_login(self):
        student_user = User.objects.create_user(username='student1', password='studentpass123')
        filiere = Filiere.objects.create(nom='Reseaux')
        Etudiant.objects.create(nom='Hajar', filiere=filiere, user=student_user)

        response = self.client.post(
            reverse('login'),
            {'username': 'student1', 'password': 'studentpass123'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('student_dashboard'))

    def test_student_can_submit_absence_justification(self):
        student_user = User.objects.create_user(username='student2', password='studentpass123')
        filiere = Filiere.objects.create(nom='Commerce')
        student = Etudiant.objects.create(nom='Sara', filiere=filiere, user=student_user)
        presence = Presence.objects.create(etudiant=student, present=False)

        self.client.login(username='student2', password='studentpass123')
        response = self.client.post(
            reverse('justify_absence', args=[presence.id]),
            {
                'reason': 'Motif medical',
                'details': 'Consultation chez le medecin',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(AbsenceJustification.objects.filter(presence=presence, reason='Motif medical').exists())

    def test_teacher_can_manage_justifications(self):
        # Create a teacher user
        teacher_user = self.user

        # Create a student and an absence with justification
        filiere = Filiere.objects.create(nom='Informatique')
        student_user = User.objects.create_user(username='student_for_justify', password='studentpass')
        student = Etudiant.objects.create(nom='Alice', filiere=filiere, user=student_user)
        presence = Presence.objects.create(etudiant=student, present=False)
        justification = AbsenceJustification.objects.create(
            presence=presence,
            reason='Maladie',
            details='Fièvre',
            status=AbsenceJustification.STATUS_PENDING,
        )

        self.client.login(username='prof', password='securepass123')

        # Teacher approves the justification
        response = self.client.post(
            reverse('manage_justifications'),
            {'justification_id': justification.id, 'action': 'approve'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        justification.refresh_from_db()
        self.assertEqual(justification.status, AbsenceJustification.STATUS_APPROVED)

    def test_student_calendar_is_ordered_by_weekday(self):
        student_user = User.objects.create_user(username='student-calendar', password='studentpass123')
        filiere = Filiere.objects.create(nom='Planning')
        Etudiant.objects.create(nom='Imane', filiere=filiere, user=student_user)

        ClassSchedule.objects.create(
            filiere=filiere,
            day_of_week='Wednesday',
            start_time=time(14, 0),
            end_time=time(16, 0),
            subject='Algorithms',
        )
        ClassSchedule.objects.create(
            filiere=filiere,
            day_of_week='Monday',
            start_time=time(9, 0),
            end_time=time(11, 0),
            subject='Databases',
        )

        self.client.login(username='student-calendar', password='studentpass123')
        response = self.client.get(reverse('calendar'))

        self.assertEqual(response.status_code, 200)
        grouped_days = response.context['calendar_sections'][0]['grouped_days']
        self.assertEqual([day['label'] for day in grouped_days], ['Lundi', 'Mercredi'])

    def test_teacher_calendar_lists_all_classes_with_schedules(self):
        self.client.login(username='prof', password='securepass123')
        filiere_a = Filiere.objects.create(nom='GI 1')
        filiere_b = Filiere.objects.create(nom='GI 2')

        ClassSchedule.objects.create(
            filiere=filiere_a,
            day_of_week='Monday',
            start_time=time(8, 30),
            end_time=time(10, 0),
            subject='Maths',
        )
        ClassSchedule.objects.create(
            filiere=filiere_b,
            day_of_week='Tuesday',
            start_time=time(10, 0),
            end_time=time(12, 0),
            subject='Reseaux',
        )

        response = self.client.get(reverse('calendar'))

        self.assertEqual(response.status_code, 200)
        section_names = [section['filiere'].nom for section in response.context['calendar_sections'] if section['total_sessions']]
        self.assertEqual(section_names, ['GI 1', 'GI 2'])

    def test_teacher_pages_render_with_clean_templates(self):
        self.client.login(username='prof', password='securepass123')
        filiere = Filiere.objects.create(nom='Design UI', salle='A2')
        Etudiant.objects.create(nom='Nadia', filiere=filiere, email='nadia@example.com')

        urls = [
            reverse('dashboard'),
            reverse('class_detail', args=[filiere.id]),
            reverse('import_students_excel', args=[filiere.id]),
            reverse('monthly_report'),
            reverse('manage_justifications'),
            reverse('calendar'),
            reverse('user_profile'),
            reverse('update_profile'),
            reverse('change_password'),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_student_pages_render_with_clean_templates(self):
        student_user = User.objects.create_user(username='student-render', password='studentpass123')
        filiere = Filiere.objects.create(nom='Classe B')
        student = Etudiant.objects.create(nom='Salma', filiere=filiere, user=student_user)
        Presence.objects.create(etudiant=student, present=False)

        self.client.login(username='student-render', password='studentpass123')
        urls = [
            reverse('student_dashboard'),
            reverse('calendar'),
            reverse('absences_classes'),
            reverse('user_profile'),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_excel_import_form_accepts_uppercase_extensions(self):
        form = ImportExcelForm(
            files={'excel_file': SimpleUploadedFile('students.XLSX', b'dummy-data')},
        )

        self.assertTrue(form.is_valid())

    def test_student_refresh_attendance_totals_recomputes_counts(self):
        filiere = Filiere.objects.create(nom='Compta')
        student = Etudiant.objects.create(nom='Nadia', filiere=filiere)
        Presence.objects.create(etudiant=student, present=True, date=now().date())
        Presence.objects.create(etudiant=student, present=False, date=now().date() - timedelta(days=1))

        student.refresh_attendance_totals()
        student.refresh_from_db()

        self.assertEqual(student.total_presences, 1)
        self.assertEqual(student.total_absences, 1)
