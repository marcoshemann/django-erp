#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This file is part of the django ERP project.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

__author__ = 'Emanuele Bertoldi <emanuele.bertoldi@gmail.com>'
__copyright__ = 'Copyright (c) 2013 Emanuele Bertoldi'
__version__ = '0.0.2'

from django.test import TestCase
from django.contrib.auth import get_user_model

from models import *
from forms import *

class ManagementInstallTestCase(TestCase):
    def test_install(self):
        """Tests app installation.
        """
        from djangoerp.core.models import Group
        from management import install
        
        install(None)
        
        users_group, is_new = Group.objects.get_or_create(name="users")

        self.assertTrue(users_group.permissions.get_by_natural_key("view_notification", "notifications", "notification"))
        
class SubscriptionsFormTestCase(TestCase):
    def test_field_creation(self):
        """Tests correct creation of fields in SubscriptionForm.
        """
        u1, n = get_user_model().objects.get_or_create(username="u1")
        s1, n = Signature.objects.get_or_create(slug="test1", title="Test1")
        s2, n = Signature.objects.get_or_create(slug="test2", title="Test2")
        s3, n = Signature.objects.get_or_create(slug="test3", title="Test3")
        
        # NOTE: only 2 signatures (without s3).
        qs = (s1, s2)
        
        f = SubscriptionsForm(u1, signatures=qs)
        
        self.assertEqual(len(f.fields), len(qs))
        for index, (name, field) in enumerate(f.fields.items()):
            self.assertEqual(name, qs[index].slug)
            self.assertTrue(isinstance(field, SubscriptionField))
            
    def test_subscription_handling(self):
        """Tests correct subscription handling.
        """
        u1, n = get_user_model().objects.get_or_create(username="u1")
        s1, n = Signature.objects.get_or_create(slug="test1", title="Test1")
        s2, n = Signature.objects.get_or_create(slug="test2", title="Test2")
        s3, n = Signature.objects.get_or_create(slug="test3", title="Test3")
        
        qs = (s1, s2, s3)
        
        f = SubscriptionsForm(u1, signatures=qs)
        
        self.assertEqual(f.fields[s1.slug].initial, {"subscribe": False, "email": False})
        self.assertEqual(f.fields[s2.slug].initial, {"subscribe": False, "email": False})
        self.assertEqual(f.fields[s3.slug].initial, {"subscribe": False, "email": False})
        
        ss1, n = Subscription.objects.get_or_create(subscriber=u1, signature=s1, send_email=True)
        ss3, n = Subscription.objects.get_or_create(subscriber=u1, signature=s3, send_email=False)
        
        f1 = SubscriptionsForm(u1, signatures=qs)
        
        self.assertEqual(f1.fields[s1.slug].initial, {"subscribe": True, "email": True})
        self.assertEqual(f1.fields[s2.slug].initial, {"subscribe": False, "email": False})
        self.assertEqual(f1.fields[s3.slug].initial, {"subscribe": True, "email": False})
        
    def test_subscription_creation(self):
        """Tests correct subscription creation.
        """
        u1, n = get_user_model().objects.get_or_create(username="u1")
        s4, n = Signature.objects.get_or_create(slug="test4", title="Test4")
        s5, n = Signature.objects.get_or_create(slug="test5", title="Test5")
        s6, n = Signature.objects.get_or_create(slug="test6", title="Test6")
        
        qs = (s4, s5, s6)
        
        self.assertEqual(Subscription.objects.filter(subscriber=u1, signature__in=qs).count(), 0)
        
        f = SubscriptionsForm(
            u1,
            {"%s_0" % s4.slug: True, "%s_1" % s4.slug: False},
            initial={s4.slug: {"subscribe": True, "email": False}},
            signatures=qs
        )

        f.save()
        
        try:
            s = Subscription.objects.get(subscriber=u1, signature=s4)
            self.assertEqual(s.signature, s4)
            self.assertEqual(s.subscriber, u1)
            self.assertEqual(s.send_email, False)
            self.assertEqual(Subscription.objects.filter(subscriber=u1, signature__in=(s5, s6)).count(), 0)
        except Subscription.DoesNotExist:
            self.assertFalse(True)
        
    def test_subscription_deletion(self):
        """Tests correct subscription deletion.
        """
        u1, n = get_user_model().objects.get_or_create(username="u1")
        s7, n = Signature.objects.get_or_create(slug="test7", title="Test7")
        
        qs = (s7,)
        
        s, n = Subscription.objects.get_or_create(subscriber=u1, signature=s7)
        
        self.assertNotEqual(Subscription.objects.filter(subscriber=u1, signature__in=qs).count(), 0)
        
        f = SubscriptionsForm(
            u1,
            {"%s_0" % s7.slug: False, "%s_1" % s7.slug: False},
            signatures=qs
        )

        f.save()
        
        self.assertEqual(Subscription.objects.filter(subscriber=u1, signature__in=qs).count(), 0)
