"""
models.py — StudentRecord model (Part C of Lab Activity 1)
"""
from django.db import models
from django.contrib.auth.models import User


class StudentRecord(models.Model):
    """
    Represents a student's academic record.
    - owner: linked Django user account (the student)
    - full_name: student's complete name
    - course: programme / degree enrolled
    - year_level: current year in programme (1-4)
    - gpa: general point average (optional)
    - created_at / updated_at: audit timestamps
    """
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='student_records',
        help_text="The student (user) this record belongs to."
    )
    full_name = models.CharField(max_length=100)
    course = models.CharField(max_length=50)
    year_level = models.IntegerField()
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']
        verbose_name = 'Student Record'
        verbose_name_plural = 'Student Records'

    def __str__(self):
        return f"{self.full_name} | {self.course} (Year {self.year_level})"
