import uuid

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import Role, UserProfile
from restaurants.models import Restaurant


def make_owner(email=None, password='testpass123', restaurant_name='Warung Test'):
    """Helper: create a staff user with owner role and a linked restaurant."""
    email = email or f'owner_{uuid.uuid4().hex[:6]}@test.com'
    username = f'owner_{uuid.uuid4().hex[:6]}'
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        is_staff=True,
    )
    slug = f'warung-{uuid.uuid4().hex[:6]}'
    restaurant = Restaurant.objects.create(
        name=restaurant_name,
        slug=slug,
        is_active=True,
    )
    profile = UserProfile.objects.create(
        user=user, restaurant=restaurant, role=Role.OWNER
    )
    return user, restaurant, profile


def make_employee(email, role, restaurant, password='testpass123'):
    """Helper: create a staff user with a non-owner role."""
    username = f'staff_{uuid.uuid4().hex[:6]}'
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        is_staff=True,
    )
    profile = UserProfile.objects.create(user=user, restaurant=restaurant, role=role)
    return user, profile


# ─── Email Backend ────────────────────────────────────────────────────────────


class EmailBackendTest(TestCase):
    """EmailBackend authenticates by email, not username."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user_abc123',
            email='test@example.com',
            password='testpass123',
            is_staff=True,
        )
        # Give user a restaurant so login redirects to dashboard not onboarding
        restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            slug='test-restaurant-abc',
            is_active=True,
        )
        UserProfile.objects.create(
            user=self.user, restaurant=restaurant, role=Role.OWNER
        )

    def test_login_with_email_succeeds(self):
        logged_in = self.client.login(
            username='test@example.com', password='testpass123'
        )
        self.assertTrue(logged_in)

    def test_login_with_wrong_email_fails(self):
        logged_in = self.client.login(
            username='wrong@example.com', password='testpass123'
        )
        self.assertFalse(logged_in)

    def test_login_with_wrong_password_fails(self):
        logged_in = self.client.login(username='test@example.com', password='wrongpass')
        self.assertFalse(logged_in)

    def test_login_via_login_view_with_email(self):
        response = self.client.post(
            reverse('login'),
            {
                'username': 'test@example.com',
                'password': 'testpass123',
            },
        )
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_via_login_view_wrong_email(self):
        response = self.client.post(
            reverse('login'),
            {
                'username': 'no@example.com',
                'password': 'testpass123',
            },
        )
        self.assertEqual(response.status_code, 200)


# ─── Registration ─────────────────────────────────────────────────────────────


class UserProfileCreationTest(TestCase):
    """UserProfile is created with correct role and restaurant on registration."""

    def test_register_creates_user_profile_with_owner_role(self):
        response = self.client.post(
            reverse('register'),
            {
                'email': 'newowner@example.com',
                'password1': 'testpass123',
                'password2': 'testpass123',
                'restaurant_name': 'Kafe Baru',
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email='newowner@example.com')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.role, Role.OWNER)

    def test_register_links_profile_to_restaurant(self):
        self.client.post(
            reverse('register'),
            {
                'email': 'ownerlinked@example.com',
                'password1': 'testpass123',
                'password2': 'testpass123',
                'restaurant_name': 'Restoran Terhubung',
            },
        )
        user = User.objects.get(email='ownerlinked@example.com')
        self.assertIsNotNone(user.profile.restaurant)
        self.assertEqual(user.profile.restaurant.name, 'Restoran Terhubung')

    def test_register_mismatched_passwords_does_not_create_user(self):
        self.client.post(
            reverse('register'),
            {
                'email': 'bad@example.com',
                'password1': 'pass1',
                'password2': 'pass2',
                'restaurant_name': 'Bad Restaurant',
            },
        )
        self.assertFalse(User.objects.filter(email='bad@example.com').exists())

    def test_register_duplicate_email_rejected(self):
        User.objects.create_user(
            username='existing_abc',
            email='dup@example.com',
            password='pass',
            is_staff=True,
        )
        response = self.client.post(
            reverse('register'),
            {
                'email': 'dup@example.com',
                'password1': 'testpass123',
                'password2': 'testpass123',
                'restaurant_name': 'Restoran Duplikat',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email='dup@example.com').count(), 1)

    def test_register_auto_generates_unique_username(self):
        self.client.post(
            reverse('register'),
            {
                'email': 'autoname@example.com',
                'password1': 'testpass123',
                'password2': 'testpass123',
                'restaurant_name': 'Auto Warung',
            },
        )
        user = User.objects.get(email='autoname@example.com')
        self.assertNotEqual(user.username, '')
        self.assertNotEqual(user.username, 'autoname@example.com')


# ─── Role Checks ──────────────────────────────────────────────────────────────


class RoleCheckTest(TestCase):
    """role_required decorator allows correct roles and blocks others."""

    def setUp(self):
        self.owner, self.restaurant, self.owner_profile = make_owner(
            email='owner@test.com'
        )
        self.kasir_user, self.kasir_profile = make_employee(
            'kasir1@test.com',
            Role.KASIR,
            self.restaurant,
        )
        self.client = Client()

    def test_owner_can_access_employee_page(self):
        self.client.login(username='owner@test.com', password='testpass123')
        response = self.client.get(reverse('employee'))
        self.assertEqual(response.status_code, 200)

    def test_kasir_cannot_access_employee_page(self):
        self.client.login(username='kasir1@test.com', password='testpass123')
        response = self.client.get(reverse('employee'))
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_redirected_from_employee_page(self):
        response = self.client.get(reverse('employee'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("employee")}')


# ─── Employee CRUD ────────────────────────────────────────────────────────────


class EmployeeCreateTest(TestCase):
    """Owner can create a new employee with a role."""

    def setUp(self):
        self.owner, self.restaurant, self.owner_profile = make_owner(
            email='owner@test.com'
        )
        self.client.login(username='owner@test.com', password='testpass123')

    def test_create_employee_creates_user_and_profile(self):
        response = self.client.post(
            reverse('employee_create'),
            {
                'email': 'kasir@warung.com',
                'password': 'staffpass123',
                'role': 'kasir',
            },
        )
        self.assertRedirects(response, reverse('employee'))
        user = User.objects.get(email='kasir@warung.com')
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.role, Role.KASIR)
        self.assertEqual(profile.restaurant, self.restaurant)

    def test_create_employee_auto_generates_username(self):
        self.client.post(
            reverse('employee_create'),
            {
                'email': 'dapur@warung.com',
                'password': 'staffpass123',
                'role': 'dapur',
            },
        )
        user = User.objects.get(email='dapur@warung.com')
        self.assertTrue(user.username.startswith(self.restaurant.slug))

    def test_create_employee_duplicate_email_shows_error(self):
        User.objects.create_user(
            username='existing_abc',
            email='existing@warung.com',
            password='pass',
            is_staff=True,
        )
        response = self.client.post(
            reverse('employee_create'),
            {
                'email': 'existing@warung.com',
                'password': 'staffpass123',
                'role': 'kasir',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email sudah digunakan')

    def test_kasir_cannot_create_employee(self):
        kasir_user, _ = make_employee(
            'kasir_creator@test.com', Role.KASIR, self.restaurant
        )
        self.client.login(username='kasir_creator@test.com', password='testpass123')
        response = self.client.post(
            reverse('employee_create'),
            {
                'email': 'new_staff@test.com',
                'password': 'newpass123',
                'role': 'kasir',
            },
        )
        self.assertEqual(response.status_code, 403)


class EmployeeUpdateTest(TestCase):
    """Owner can update employee role and active status."""

    def setUp(self):
        self.owner, self.restaurant, self.owner_profile = make_owner(
            email='owner@test.com'
        )
        self.staff_user, self.staff_profile = make_employee(
            'staff1@test.com',
            Role.KASIR,
            self.restaurant,
        )
        self.client.login(username='owner@test.com', password='testpass123')

    def test_update_employee_role(self):
        self.client.post(
            reverse('employee_update', kwargs={'pk': self.staff_profile.pk}),
            {'role': 'dapur', 'is_active': 'on'},
        )
        self.staff_profile.refresh_from_db()
        self.assertEqual(self.staff_profile.role, Role.DAPUR)

    def test_deactivate_employee(self):
        self.client.post(
            reverse('employee_update', kwargs={'pk': self.staff_profile.pk}),
            {'role': 'kasir'},
        )
        self.staff_user.refresh_from_db()
        self.assertFalse(self.staff_user.is_active)

    def test_reactivate_employee(self):
        self.staff_user.is_active = False
        self.staff_user.save()
        self.client.post(
            reverse('employee_update', kwargs={'pk': self.staff_profile.pk}),
            {'role': 'kasir', 'is_active': 'on'},
        )
        self.staff_user.refresh_from_db()
        self.assertTrue(self.staff_user.is_active)


class EmployeeDeleteTest(TestCase):
    """Owner can delete an employee and their user account."""

    def setUp(self):
        self.owner, self.restaurant, self.owner_profile = make_owner(
            email='owner@test.com'
        )
        self.staff_user, self.staff_profile = make_employee(
            'staff_del@test.com',
            Role.ADMIN,
            self.restaurant,
        )
        self.client.login(username='owner@test.com', password='testpass123')

    def test_delete_removes_user_and_profile(self):
        pk = self.staff_profile.pk
        user_pk = self.staff_user.pk
        response = self.client.post(
            reverse('employee_delete', kwargs={'pk': pk}),
        )
        self.assertRedirects(response, reverse('employee'))
        self.assertFalse(User.objects.filter(pk=user_pk).exists())
        self.assertFalse(UserProfile.objects.filter(pk=pk).exists())

    def test_non_owner_cannot_delete_employee(self):
        kasir_user, _ = make_employee('kasir_del@test.com', Role.KASIR, self.restaurant)
        self.client.login(username='kasir_del@test.com', password='testpass123')
        response = self.client.post(
            reverse('employee_delete', kwargs={'pk': self.staff_profile.pk}),
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(User.objects.filter(pk=self.staff_user.pk).exists())


class OwnerSelfDeleteProtectionTest(TestCase):
    """Owner cannot delete their own account via the employee delete endpoint."""

    def setUp(self):
        self.owner, self.restaurant, self.owner_profile = make_owner(
            email='owner@test.com'
        )
        self.client.login(username='owner@test.com', password='testpass123')

    def test_owner_cannot_delete_themselves(self):
        response = self.client.post(
            reverse('employee_delete', kwargs={'pk': self.owner_profile.pk}),
        )
        self.assertRedirects(response, reverse('employee'))
        self.assertTrue(User.objects.filter(email='owner@test.com').exists())


class CrossRestaurantAccessTest(TestCase):
    """Owner from Restaurant A cannot modify or delete staff from Restaurant B."""

    def setUp(self):
        self.owner_a, self.restaurant_a, _ = make_owner(
            email='owner_a@test.com',
            restaurant_name='Warung A',
        )
        self.owner_b, self.restaurant_b, _ = make_owner(
            email='owner_b@test.com',
            restaurant_name='Warung B',
        )
        self.staff_b, self.profile_b = make_employee(
            'staff_b@test.com',
            Role.KASIR,
            self.restaurant_b,
        )
        self.client.login(username='owner_a@test.com', password='testpass123')

    def test_owner_a_cannot_delete_staff_from_restaurant_b(self):
        response = self.client.post(
            reverse('employee_delete', kwargs={'pk': self.profile_b.pk}),
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(User.objects.filter(pk=self.staff_b.pk).exists())

    def test_owner_a_cannot_update_staff_from_restaurant_b(self):
        response = self.client.post(
            reverse('employee_update', kwargs={'pk': self.profile_b.pk}),
            {'role': 'dapur', 'is_active': 'on'},
        )
        self.assertEqual(response.status_code, 404)
        self.profile_b.refresh_from_db()
        self.assertEqual(self.profile_b.role, Role.KASIR)
