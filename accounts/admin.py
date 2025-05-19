from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Role, Permission, Profile, Client, Employee

# Retirez complètement les inlines de Client et Employee pour l'admin User
# Gardez uniquement le ProfileInline
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profil'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_select_related = ('profile',)
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__phone')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    
    def get_role(self, obj):
        if hasattr(obj, 'profile') and obj.profile and hasattr(obj.profile, 'role') and obj.profile.role:
            return obj.profile.role.name
        return 'Aucun rôle'
    get_role.short_description = 'Rôle'

# Désinscrire l'administration utilisateur par défaut
admin.site.unregister(User)
# Enregistrer l'administration utilisateur personnalisée
admin.site.register(User, CustomUserAdmin)

# Admin pour Profile avec inlines pour Client et Employee
class ClientInline(admin.StackedInline):
    model = Client
    can_delete = False
    verbose_name_plural = 'Client'

class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'Employé'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'role', 'date_joined')
    list_filter = ('role', 'date_joined')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone')
    
    def get_inlines(self, request, obj):
        if not obj:
            return []
        
        if obj.role:
            if obj.role.name == 'Client':
                return [ClientInline]
            elif obj.role.name in ['Réceptionniste', 'Manager', 'Administrateur']:
                return [EmployeeInline]
        
        return []

# Rôles et permissions
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    filter_horizontal = ('roles',)

# Modèles Client et Employee
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_email', 'is_loyal', 'loyalty_points')
    search_fields = ('profile__user__username', 'profile__user__email')
    list_filter = ('is_loyal',)
    
    def get_username(self, obj):
        return obj.profile.user.username if obj.profile and obj.profile.user else ""
    get_username.short_description = "Nom d'utilisateur"
    
    def get_email(self, obj):
        return obj.profile.user.email if obj.profile and obj.profile.user else ""
    get_email.short_description = "Email"

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_email', 'position', 'hire_date', 'employee_id')
    search_fields = ('profile__user__username', 'profile__user__email', 'position')
    list_filter = ('position', 'hire_date')
    
    def get_username(self, obj):
        return obj.profile.user.username if obj.profile and obj.profile.user else ""
    get_username.short_description = "Nom d'utilisateur"
    
    def get_email(self, obj):
        return obj.profile.user.email if obj.profile and obj.profile.user else ""
    get_email.short_description = "Email"