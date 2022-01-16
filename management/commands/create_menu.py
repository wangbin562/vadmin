# !/usr/bin/python
# -*- coding=utf-8 -*-

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **options):
        from vadmin import menu

        # menu.init_menu_permission()
        print('Create menu successfully!')
