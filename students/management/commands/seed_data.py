"""
seed_data.py — Management command that creates demo users and sample records.
Run with: python manage.py seed_data

Creates:
  Groups  : Admin, Faculty, Student
  Users   : admin_user / faculty_user / student_alice / student_bob
  Records : 4 sample student records
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from students.models import StudentRecord


GROUPS = ['Admin', 'Faculty', 'Student']

USERS = [
    {
        'username': 'admin_user',
        'email': 'admin@school.edu',
        'password': 'AdminPass123',
        'first_name': 'Admin',
        'last_name': 'User',
        'role': 'Admin',
        'is_staff': True,
    },
    {
        'username': 'faculty_user',
        'email': 'faculty@school.edu',
        'password': 'FacultyPass123',
        'first_name': 'Faculty',
        'last_name': 'User',
        'role': 'Faculty',
    },
    {
        'username': 'student_alice',
        'email': 'alice@school.edu',
        'password': 'AlicePass123',
        'first_name': 'Alice',
        'last_name': 'Reyes',
        'role': 'Student',
    },
    {
        'username': 'student_bob',
        'email': 'bob@school.edu',
        'password': 'BobPass123',
        'first_name': 'Bob',
        'last_name': 'Santos',
        'role': 'Student',
    },
]

RECORDS = [
    {
        'owner_username': 'student_alice',
        'full_name': 'Alice Reyes',
        'course': 'BSIT',
        'year_level': 3,
        'gpa': 1.75,
    },
    {
        'owner_username': 'student_bob',
        'full_name': 'Bob Santos',
        'course': 'BSCS',
        'year_level': 2,
        'gpa': 2.00,
    },
    {
        'owner_username': 'student_alice',
        'full_name': 'Alice Reyes (Elective)',
        'course': 'BSIT Elective',
        'year_level': 3,
        'gpa': 1.50,
    },
    {
        'owner_username': 'student_bob',
        'full_name': 'Bob Santos (Lab)',
        'course': 'BSCS Laboratory',
        'year_level': 2,
        'gpa': 1.25,
    },
]


class Command(BaseCommand):
    help = 'Seeds the database with demo users and sample student records.'

    def handle(self, *args, **kwargs):
        # 1. Create groups
        for g_name in GROUPS:
            group, created = Group.objects.get_or_create(name=g_name)
            self.stdout.write(
                self.style.SUCCESS(f"  {'Created' if created else 'Exists'} group: {g_name}")
            )

        # 2. Create users and assign groups
        for u in USERS:
            role = u.pop('role')
            is_staff = u.pop('is_staff', False)
            password = u.pop('password')

            user, created = User.objects.get_or_create(
                username=u['username'],
                defaults={**u, 'is_staff': is_staff}
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"  Created user: {user.username}"))
            else:
                self.stdout.write(f"  Exists user: {user.username}")

            group = Group.objects.get(name=role)
            user.groups.add(group)

        # 3. Create student records
        for rec in RECORDS:
            owner = User.objects.get(username=rec.pop('owner_username'))
            record, created = StudentRecord.objects.get_or_create(
                owner=owner,
                full_name=rec['full_name'],
                defaults=rec,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"  {'Created' if created else 'Exists'} record: {record}"
                )
            )

        self.stdout.write(self.style.SUCCESS('\n[OK] Seed complete!'))
        self.stdout.write(self.style.WARNING(
            '\nDemo credentials:\n'
            '  admin_user    / AdminPass123\n'
            '  faculty_user  / FacultyPass123\n'
            '  student_alice / AlicePass123\n'
            '  student_bob   / BobPass123\n'
        ))
