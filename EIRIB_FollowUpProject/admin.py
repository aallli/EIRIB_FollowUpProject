from django.contrib import admin
from django.db.transaction import atomic
from EIRIB_FollowUpProject.utils import execute_query
from django.contrib.auth import password_validation
from django import forms
from django.utils.translation import ugettext_lazy as _


class AdminSite(admin.AdminSite):
    @atomic()
    def password_change(self, request, extra_context=None):
        response = super(AdminSite, self).password_change(request, extra_context=None)
        if request.method == 'POST' and (response.status_code == 302 or 'class="errornote"' not in response.rendered_content):
            password = request.POST['new_password1']
            query = '''
                    UPDATE tblUser
                    SET Password = ?
                    WHERE LName = ?
                   '''
            params = (password, request.user.username)
            execute_query(query, params, True)
        return response
