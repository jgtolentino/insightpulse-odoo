# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from pathlib import Path

from lxml import etree
from odoo_test_helper import FakeModelLoader

from odoo.addons.data_encryption.tests.common import CommonDataEncrypted


class TestServerEnvDataEncrypted(CommonDataEncrypted):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()

        # The fake class is imported here !! After the backup_registry
        from .models import FakePartner

        cls.loader.update_registry((FakePartner,))
        cls.set_new_key_env("prod")
        cls.set_new_key_env("preprod")

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def test_env_dependent_value(self):
        partner = self.env["res.partner"].create(
            {"name": "Fake name", "city": "test city"}
        )
        self.assertFalse(partner.with_context(environment="prod").city)
        partner.with_context(environment="prod").write({"city": "prod city"})
        self.assertEqual(partner.with_context(environment=False).city, "test city")
        self.assertEqual(partner.with_context(environment="test").city, "test city")
        self.assertEqual(partner.with_context(environment="prod").city, "prod city")

    def test_view_with_env_update(self):
        self.maxDiff = None
        # common class already set test environment (as default)
        mixin_obj = self.env["server.env.mixin"]
        base_path = Path(__file__).parent / "fixtures" / "base.xml"
        xml_str = base_path.read_text()
        xml = etree.XML(xml_str)
        res_xml = mixin_obj._update_form_view_from_env(xml, "form")

        # check we have 3 alert div for our 3 environments
        env_div_xml = res_xml.find("sheet").find("div").findall("div")
        # 3 alert div + 1 button div
        self.assertEqual(len(env_div_xml), 4)
        # test first alert test div
        test_alert_div = env_div_xml[0]
        self.assertEqual(
            test_alert_div.get("invisible"),
            "context.get('environment', 'test') != 'test'",
        )
        self.assertEqual(
            test_alert_div.find("strong").text, "Modify values for test environment"
        )
        # test preprod div
        preprod_alert_div = env_div_xml[1]
        self.assertEqual(
            preprod_alert_div.get("invisible"),
            "context.get('environment', 'test') != 'preprod'",
        )
        self.assertEqual(
            preprod_alert_div.find("strong").text,
            "Modify values for preprod environment",
        )
        # test buttons
        button_div = env_div_xml[-1]
        # 3 buttons for 3 env
        self.assertEqual(len(button_div.findall("button")), 3)
        test_button = button_div.findall("button")[0]
        # test env button
        self.assertEqual(
            test_button.get("invisible"), "context.get('environment', 'test') == 'test'"
        )
        self.assertEqual(
            test_button.get("name"), "action_change_env_data_encrypted_fields"
        )
        self.assertEqual(test_button.get("string"), "Define values for test")
        # preprod button
        preprod_button = button_div.findall("button")[1]
        self.assertEqual(
            preprod_button.get("invisible"),
            "context.get('environment', 'test') == 'preprod'",
        )
        self.assertEqual(preprod_button.get("string"), "Define values for preprod")
        self.assertEqual(preprod_button.get("context"), "{'environment': 'preprod'}")
        # test normal field with pre-existing readonly condition
        test2_field = res_xml.find("sheet").findall(".//field[@name='test2']")[0]
        self.assertEqual(
            test2_field.get("readonly"),
            "(not type_env_is_editable) or context.get(\"environment\", 'test') != "
            "'test'",
        )
        # test normal field without pre-existing readonly condition
        test_field = res_xml.find("sheet").findall(".//field[@name='test']")[0]
        self.assertEqual(
            test_field.get("readonly"), "context.get(\"environment\", 'test') != 'test'"
        )

        # test that buttons are invisible in the context of env different than the
        # running one.
        confirm_button = res_xml.find("header").find("button")
        self.assertEqual(
            confirm_button.get("invisible"),
            "context.get(\"environment\", 'test') != 'test'",
        )
